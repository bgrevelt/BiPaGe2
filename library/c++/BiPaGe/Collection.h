#pragma once
#include <type_traits>
#include <string>
#include <sstream>
#include <type_traits>
#include <iterator>
#include <cstddef>
#include <sstream>

#include "Endianness.h"

namespace BiPaGe
{
    template<typename T>
    T deref_little_endian(const T* p)
    {
        return *p;
    }

    template<typename T>
    T deref_big_endian(const T* p)
    {
        return swap_bytes(*p);
    }

    template<typename T, T (*DEREF)(const T*)>
    struct Iterator
    {
    public:
        using iterator_category = std::random_access_iterator_tag;
        using difference_type   = std::ptrdiff_t;
        using value_type        = T;
        using pointer           = const T*;
        using reference         = T;

        Iterator(pointer ptr) : m_ptr(ptr) {}

        // Prefix in/decrement
        Iterator& operator++() { m_ptr++; return *this; }
        Iterator& operator--() { m_ptr--; return *this; }

        // Postfix in/decrement
        Iterator operator++(int) { Iterator tmp = *this; ++(*this); return tmp; }
        Iterator operator--(int) { Iterator tmp = *this; --(*this); return tmp; }

        Iterator operator+(int rhs) {return Iterator(m_ptr+rhs);}
        Iterator operator-(int rhs) {return Iterator(m_ptr-rhs);}
        Iterator operator+=(int rhs) {m_ptr += rhs; return *this;}
        Iterator operator-=(int rhs) {m_ptr += rhs; return *this;}

        friend bool operator== (const Iterator& a, const Iterator& b) { return a.m_ptr == b.m_ptr; }
        friend bool operator!= (const Iterator& a, const Iterator& b) { return a.m_ptr != b.m_ptr; }
        friend bool operator< (const Iterator& a, const Iterator& b) { return a.m_ptr < b.m_ptr; }
        friend bool operator<= (const Iterator& a, const Iterator& b) { return a.m_ptr <= b.m_ptr; }
        friend bool operator> (const Iterator& a, const Iterator& b) { return a.m_ptr > b.m_ptr; }
        friend bool operator>= (const Iterator& a, const Iterator& b) { return a.m_ptr >= b.m_ptr; }

        reference operator*() const { return DEREF(this->m_ptr); }
        reference operator[](int rhs) {return DEREF(this->m_ptr + rhs);}

    protected:
        pointer m_ptr;
    };

    template<typename T>
    struct IteratorBigEndian : public Iterator<T,deref_big_endian>
    {
        IteratorBigEndian(typename Iterator<T,deref_big_endian>::pointer p) : Iterator<T,deref_big_endian>(p) {}
    };

    template<typename T>
    struct IteratorLittleEndian : public Iterator<T,deref_little_endian>
    {
        IteratorLittleEndian(typename Iterator<T,deref_little_endian>::pointer p) : Iterator<T,deref_little_endian>(p) {}
    };

    template<typename T, template<typename> class ITERATOR_TYPE, typename Enable=void>
    class Collection;

    template<typename T, template<typename> class ITERATOR_TYPE>
    class Collection<T, ITERATOR_TYPE, typename std::enable_if<std::is_integral<T>::value || std::is_floating_point<T>::value || std::is_enum<T>::value, void>::type>
    {
    public:
        Collection(const void* data, size_t size)
            : data_(reinterpret_cast<const T*>(data))
            , size_(size)
        {

        }

        ITERATOR_TYPE<T> begin() const
        {
            return ITERATOR_TYPE<T>(data_);
        }
        ITERATOR_TYPE<T> end() const
        {
            return ITERATOR_TYPE<T>(data_ + size_);
        }
        T at(size_t index) const
        {
            return *(begin() + static_cast<int>(index));
        }
        T back() const
        {
            return *(begin() + size_ -1);
        }
        T front() const
        {
            return *begin();
        }
        size_t size() const
        {
            return size_;
        }
        T operator[](size_t index) const
        {
            return at(index);
        }
    private:
        const T* data_;
        const size_t size_;
    };

    template<typename T>
    class CollectionLittleEndian : public Collection<T, IteratorLittleEndian>
    {
    public:
        CollectionLittleEndian(const void* data, size_t size): Collection<T, IteratorLittleEndian>(data, size)
        {

        }
    };

    template<typename T>
    class CollectionBigEndian : public Collection<T, IteratorBigEndian>
    {
    public:
        CollectionBigEndian(const void* data, size_t size): Collection<T, IteratorBigEndian>(data, size)
        {

        }
    };
}
