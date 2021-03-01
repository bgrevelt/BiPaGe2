#pragma once
#include <type_traits>
#include <string>
#include <sstream>

namespace BiPaGe
{
    template<typename T, size_t COLLECTION_SIZE, typename Enable=void>
    class Collection;

    template<typename T, size_t COLLECTION_SIZE>
    class Collection<T,COLLECTION_SIZE, typename std::enable_if<std::is_pod<T>::value, void>::type>
    {
    public:
        Collection(const void* data)
            : data_(reinterpret_cast<const T*>(data))
        {

        }

        const T* begin() const
        {
            return data_;
        }
        const T* end() const
        {
            return begin() + COLLECTION_SIZE;
        }
        const T& at(size_t index) const
        {
            assert(index < COLLECTION_SIZE);
            return *(begin() + index);
        }
        const T& back() const
        {
            return *(begin() + COLLECTION_SIZE -1);
        }
        const T& front() const
        {
            return *begin();
        }
        size_t size() const
        {
            return COLLECTION_SIZE;
        }
        const T& operator[](size_t index) const
        {
            return at(index);
        }
        std::string to_string() const
        {
            std::stringstream ss;
            ss << "[ ";
            for(auto current = begin() ; current < end() ; ++current)
                ss << *current << (current < (end()-1) ? ", " : "");
            ss << " ]";
            return ss.str();
        }
    private:
        const T* const data_;
    };
}