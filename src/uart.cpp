#include "libhal-atmega/uart.hpp"
#include "libhal-atmega/mcu.hpp"
#include "status_lock.hpp"
#include <array>
#include <avr/interrupt.h>
#include <avr/io.h>
#include <cstdint>
#include <libhal/units.hpp>
#include <stdexcept>

namespace {
struct BaudEntry
{
  hal::hertz frequency;
  uint16_t value;
  bool u2x;
};
#if F_CPU == 16000000
// copied straight from
// https://ww1.microchip.com/downloads/en/DeviceDoc/Atmel-7810-Automotive-Microcontrollers-ATmega328P_Datasheet.pdf
constexpr auto baud_table =
  std::to_array<BaudEntry>({ { 9600.f, 103, false },
                             { 4800.f, 207, false },
                             { 2400.f, 416, false },
                             { 14400.f, 138, true },
                             { 19200.f, 51, false },
                             { 28800.f, 68, true },
                             { 38400.f, 25, false },
                             { 57600.f, 34, true },
                             { 76800.f, 12, false },
                             { 115200.f, 16, true },
                             { 250000.f, 3, false } });
#endif

union UARTB
{
  struct
  {
    bool tx_bit8 : 1, rx_bit8 : 1, size2 : 1, tx_en : 1, rx_en : 1, udr_ie : 1,
      txc_ie : 1, rxc_ie : 1;
  };
  uint8_t byte;
};

union UARTC
{
  struct
  {
    uint8_t polarity : 1, size : 2, stop : 1, parity : 2, mode : 2;
  };
  uint8_t byte;
};

}  // namespace
namespace hal::atmega {

uart::uart(std::span<uint8_t> p_in_buffer,
           std::span<uint8_t> p_out_buffer,
           uint8_t index)
  : m_rx(p_in_buffer.begin(), p_in_buffer.end())
  , m_tx(p_out_buffer.begin(), p_out_buffer.end())
  , m_index(index)
{
  if (uart_impl::global_uart[index] != nullptr)
    throw std::runtime_error("You constructed UART twice");

  uart_impl::global_uart[index] = this;
  sei();
}

uart::~uart()
{
  slock lock;
  uart_impl::_clear(m_index);
  uart_impl::global_uart[m_index] = nullptr;
}

void uart::driver_configure(settings const& options)
{
  UARTB rb = {};
  rb.rx_en = true;
  rb.tx_en = true;
  rb.udr_ie = true;
  rb.rxc_ie = true;
  UARTC rc = {};
  rc.size = 3;
  rc.mode = 0;  // Maybe add settings for synchronous USART later
  if (options.stop == settings::stop_bits::two)
    rc.stop = 1;
  if (options.parity == settings::parity::even)
    rc.parity = 2;
  else if (options.parity == settings::parity::odd)
    rc.parity = 3;
  for (const BaudEntry& entry : baud_table) {
    if (entry.frequency == options.baud_rate) {
      uart_impl::_set_baud(m_index, entry.value, entry.u2x);
      break;
    }
  }
  uart_impl::_configure(m_index, rb.byte, rc.byte);
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
