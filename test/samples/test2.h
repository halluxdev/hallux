// Here is test1.h file

#ifndef HALLUX_TEST1_H
#define HALLUX_TEST1_H

namespace test1
{

class SomeClass
{
public:
  SomeClass() = default;
  int someFiled1;
  float someFiled2;
  int* someMethod(int arg1, float arg2)
  {
    return &arg1;
  }
};

} //namespace test1

#endif  // HALLUX_TEST1_H
