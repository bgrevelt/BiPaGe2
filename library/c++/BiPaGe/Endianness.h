#pragma once

namespace BiPaGe
{
template <typename T, size_t n>
struct SwapBytesImpl;

template <typename T>
struct SwapBytesImpl<T, 2>
{
  T operator()(const T& val) const
  {
      auto asuint = *reinterpret_cast<const std::uint16_t*>(&val);
      auto b0 = (asuint & 0xff00) >> 8;
      auto b1 = (asuint & 0x00ff) << 8;

      return static_cast<T>(b1 | b0);
  }
};

template <typename T>
struct SwapBytesImpl<T, 4>
{
  T operator()(const T& val) const
  {
#if defined(__llvm__) || (defined(__GNUC__) && !defined(__ICC))
      auto swapped = __builtin_bswap32(*reinterpret_cast<const std::uint32_t*>(&val));
      return *reinterpret_cast<T*>(&swapped);
#elif defined(_MSC_VER) && !defined(_DEBUG)
      auto swapped = _byteswap_ulong(*reinterpret_cast<const std::uint32_t*>(&val));
      return *reinterpret_cast<T*>(&swapped);
#else
      auto asuint = *reinterpret_cast<const std::uint32_t*>(&val);
      auto b0 = (asuint & 0xff000000) >> 24;
      auto b1 = (asuint & 0x00ff0000) >> 8;
      auto b2 = (asuint & 0x0000ff00) << 8;
      auto b3 = (asuint & 0x000000ff) << 24;

      return static_cast<T>(b3 | b2 | b1 | b0);
#endif
  }
};

template <typename T>
struct SwapBytesImpl<T, 8>
{
  T operator()(const T& val) const
  {
#if defined(__llvm__) || (defined(__GNUC__) && !defined(__ICC))
      auto swapped = __builtin_bswap64(*reinterpret_cast<const std::uint64_t*>(&val));
      return *reinterpret_cast<T*>(&swapped);
#elif defined(_MSC_VER) && !defined(_DEBUG)
      auto swapped = _byteswap_uint64(*reinterpret_cast<const std::uint64_t*>(&val));
      return *reinterpret_cast<T*>(&swapped);
#else
      auto asuint = *reinterpret_cast<const std::uint64_t*>(&val);
      auto b0 = (asuint & 0xff00000000000000) >> 56;
      auto b1 = (asuint & 0x00ff000000000000) >> 40;
      auto b2 = (asuint & 0x0000ff0000000000) >> 24;
      auto b3 = (asuint & 0x000000ff00000000) >> 8;
      auto b4 = (asuint & 0x00000000ff000000) << 8;
      auto b5 = (asuint & 0x0000000000ff0000) << 24;
      auto b6 = (asuint & 0x000000000000ff00) << 40;
      auto b7 = (asuint & 0x00000000000000ff) << 56;

      return *reinterpret_cast<T*>(b7 | b6 | b5 | b4 | b3 | b2 | b1 | b0);
#endif
  }
};

template <typename T>
T swap_bytes(T val)
{
    return SwapBytesImpl<T, sizeof(T)>()(val);
}
}
