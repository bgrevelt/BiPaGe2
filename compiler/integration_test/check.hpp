#pragma once

#define check_equal(l,r) check_equal_func(l,r,__FUNCTION__, __LINE__)

template<typename T1, typename T2>
void check_equal_func(const T1& l, const T2& r, const char* caller, int line)
{
    if(l != r)
    {
        std::cerr << "check_equal called from " << caller << ", line " << line << ": " << l << " is not equal to " << r << std::endl;
        exit(-1);
    }
}

template<typename T>
std::uint8_t* serialize(std::uint8_t* data, T value)
{
    *reinterpret_cast<T*>(data) = value;
    return data + sizeof(T);
}