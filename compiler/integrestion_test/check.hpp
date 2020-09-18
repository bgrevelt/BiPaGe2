#pragma once

template<typename T1, typename T2>
void check_equal(const T1& l, const T2& r)
{
    if(l != r)
    {
        std::cout << l << " is not equal to " << r << std::endl;
        exit(-1);
    }
}

template<typename T>
std::uint8_t* serialize(std::uint8_t* data, T value)
{
    *reinterpret_cast<T*>(data) = value;
    return data + sizeof(T);
}