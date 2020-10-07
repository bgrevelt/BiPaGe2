#pragma once
#include <algorithm>
#include <functional>
#include <iostream>

#define check_equal(l,r) check_equal_func(l,r,__FUNCTION__, __LINE__)
#define check_exception(e,f) check_exception_func<e>(f,__FUNCTION__, __LINE__, #e)
#define check_type(e,v) check_type_func<e>(v,__FUNCTION__, __LINE__, #e)


template<typename T1, typename T2>
void check_equal_func(const T1& l, const T2& r, const char* caller, int line)
{
    if(l != r)
    {
        std::cerr << "check_equal called from " << caller << ", line " << line << ": " << +l << " is not equal to " << +r << std::endl;
        exit(-1);
    }
}

template<typename T1, typename T2>
void check_equal_func(const std::vector<T1>& l, const std::vector<T2>& r, const char* caller, int line)
{
    if(l.size() != r.size())
    {
        std::cerr << "check_equal called from " << caller << ", line " << line << ": Vector L size " << l.size() << " is not equal to R size " << r.size() << std::endl;
        exit(-1);
    }
    if(!std::equal(l.begin(), l.end(), r.begin()))
    {
        std::cerr << "check_equal called from " << caller << ", line " << line << ": Two vectors are not equal:" << std::endl;
        for(size_t i = 0 ; i < l.size() ; ++i)
        {
            std::cerr << +l[i] << " " << +r[i];
            if(l[i] != r[i])
            {
                std::cerr << " <--";
            }
            std::cerr << std::endl;
        }
        exit(-1);
    }
}

template<typename ExceptionType>
void check_exception_func(std::function<void()>f, const char* caller, int line, const char* expected)
{
    try
    {
        f();
        std::cerr << "check_exception called from " << caller << ", line " << line << ": expected \"" << expected << "\" wasn't thrown" << std::endl;
        exit(-1);
    }
    catch(const ExceptionType&)
    {
    }
}

template<typename EXPECTED, typename ACTUAL>
void check_type_func(ACTUAL val, const char* caller, int line, const char* expected)
{
    if(!std::is_same<decltype(val), EXPECTED>::value)
    {
        std::cerr << "check_type called from " << caller << ", line " << line << ": type does not match expected type " << expected << std::endl;
        exit(-1);
    }
}

template<typename T>
std::uint8_t* serialize(std::uint8_t* data, T value)
{
    *reinterpret_cast<T*>(data) = value;
    return data + sizeof(T);
}