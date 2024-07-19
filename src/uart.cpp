#include "libhal-atmega/uart.hpp"
#include "status_lock.hpp"
#include <avr/interrupt.h>
#include <avr/io.h>
#include <cstdint>
#include <stdexcept>
#ifndef F_CPU
#define F_CPU 16'000'000UL
#endif

#ifndef BAUD
#define BAUD 9600
#endif
#include <util/delay.h>
#include <util/setbaud.h>

namespace {
// might have to make this volatile. maybe
hal::atmega::uart* global_uart[1] = {};

}  // namespace

namespace hal::atmega {

uart::uart(std::span<uint8_t> p_in_buffer,
           std::span<uint8_t> p_out_buffer,
           hertz p_frequency,
           uint8_t index)
  : m_rx(p_in_buffer.begin(), p_in_buffer.end())
  , m_tx(p_out_buffer.begin(), p_out_buffer.end())
  , m_frequency(p_frequency)
  , m_index(index)
{
  if (global_uart[index] != nullptr)
    throw std::runtime_error("You constructed UART twice");

  // TODO: change baud calculations to runtime
  UBRR0H = UBRRH_VALUE;
  UBRR0L = UBRRL_VALUE;

#if USE_2X
  UCSR0A |= _BV(U2X0);
#else
  UCSR0A &= ~(_BV(U2X0));
#endif

  UCSR0C = _BV(UCSZ01) | _BV(UCSZ00); /* 8-bit data */
  UCSR0B =
    _BV(RXEN0) | _BV(TXEN0) | _BV(UDRE0) | _BV(RXCIE0); /* Enable RX and TX */
  global_uart[index] = this;
  sei();
}

ISR(USART_RX_vect)
{
  auto& uart = global_uart[0];
  if (uart->m_rx.full()) {
    uart->overwritten = true;
    uart->m_rx.pop_front();
  }
  uint8_t data = UDR0;
  uart->m_rx.push_back(data);
}

ISR(USART_UDRE_vect)
{
  auto& uart = global_uart[0];
  if (uart->m_tx.empty()) {
    UCSR0A &= ~(_BV(UDRE0));
  } else {
    UDR0 = uart->m_tx.pop_front();
  }
}

uart::~uart()
{
  loop_until_bit_is_set(UCSR0A, TXC0);
  slock lock;
  UCSR0B = 0;
  UCSR0C = 0;
  global_uart[m_index] = nullptr;
}

void uart::driver_configure(settings const&)
{
  // auto baud_result = uint16_t(m_frequency / (p_settings.baud_rate * 16) - 1);
  // if (baud_result & 0b1111'0000'0000'0000) {
  //   throw std::logic_error("Baud is too low!");
  // }
}

serial::write_t uart::driver_write(std::span<const hal::byte> in)
{

  slock lock;
  uint8_t transmitted = 0;

  while (!m_tx.full() && transmitted != in.size()) {
    m_tx.push_back(in[transmitted++]);
  }

  driver_flush();
  return { in };
}

serial::read_t uart::driver_read(std::span<hal::byte> out)
{
  uint8_t transmitted = 0;

  slock lock;
  while (!m_rx.empty() && transmitted != out.size()) {
    out[transmitted++] = m_rx.pop_front();
  }

  return { out.subspan(0, transmitted), m_rx.size(), m_rx.capacity() };
}

void uart::driver_flush()
{
  UCSR0B |= _BV(UDRE0);
  if (!m_tx.empty())
    UDR0 = m_tx.pop_front();
}

}  // namespace hal::atmega
