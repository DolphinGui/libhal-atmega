#pragma once

#include <ios>
#include <libhal/serial.hpp>
#include <nonstd/ring_span.hpp>
#include <span>

// Some USART peripherals have DTR and CTS config, but most don't
// unless there's a need for it, I'll leave it out for now
namespace hal::atmega {
class uart final : public hal::serial
{
public:
  uart(std::span<uint8_t> p_in_buffer,
       std::span<uint8_t> p_out_buffer,
       uint8_t index = 0);
  ~uart();

  uart(uart const& p_other) = delete;
  uart& operator=(uart const& p_other) = delete;
  uart(uart&& p_other) noexcept;
  uart& operator=(uart&& p_other) noexcept;

  bool bad = false;
  bool overwritten = false;

  nonstd::ring_span<uint8_t> m_rx, m_tx;
private:
  void driver_configure(settings const& p_settings) override;
  write_t driver_write(std::span<const hal::byte> p_data) override;
  read_t driver_read(std::span<hal::byte> p_data) override;
  void driver_flush() override;

  void setup_receive_interrupt();

  uint8_t m_index;
};
}  // namespace hal::atmega