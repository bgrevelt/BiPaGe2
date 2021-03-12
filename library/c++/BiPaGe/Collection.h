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

    template<typename T, template<typename> class ITERATOR_TYPE, size_t COLLECTION_SIZE, typename Enable=void>
    class Collection;

    template<typename T, template<typename> class ITERATOR_TYPE, size_t COLLECTION_SIZE>
    class Collection<T, ITERATOR_TYPE, COLLECTION_SIZE, typename std::enable_if<std::is_integral<T>::value || std::is_floating_point<T>::value || std::is_enum<T>::value, void>::type>
    {
    public:
        Collection(const void* data)
            : data_(reinterpret_cast<const T*>(data))
        {

        }

        ITERATOR_TYPE<T> begin() const
        {
            return ITERATOR_TYPE<T>(data_);
        }
        ITERATOR_TYPE<T> end() const
        {
            return ITERATOR_TYPE<T>(data_ + COLLECTION_SIZE);
        }
        T at(size_t index) const
        {
            return *(begin() + static_cast<int>(index));
        }
        T back() const
        {
            return *(begin() + COLLECTION_SIZE -1);
        }
        T front() const
        {
            return *begin();
        }
        size_t size() const
        {
            return COLLECTION_SIZE;
        }
        T operator[](size_t index) const
        {
            return at(index);
        }
    private:
        const T* data_;
    };

    template<typename T, size_t COLLECTION_SIZE>
    class CollectionLittleEndian : public Collection<T, IteratorLittleEndian, COLLECTION_SIZE>
    {
    public:
        CollectionLittleEndian(const void* data): Collection<T, IteratorLittleEndian, COLLECTION_SIZE>(data)
        {

        }
    };

    template<typename T, size_t COLLECTION_SIZE>
    class CollectionBigEndian : public Collection<T, IteratorBigEndian, COLLECTION_SIZE>
    {
    public:
        CollectionBigEndian(const void* data): Collection<T, IteratorBigEndian, COLLECTION_SIZE>(data)
        {

        }
    };
}
