/*eslint constructor-super: "error"*/
/*eslint-env es6*/
// https://eslint.org/docs/latest/rules/constructor-super

class A {
  constructor() {
      super();  // This is a SyntaxError.
  }
}

class A extends B {
  constructor() { }  // Would throw a ReferenceError.
}

// Classes which inherits from a non constructor are always problems.
class A extends null {
  constructor() {
      super();  // Would throw a TypeError.
  }
}

class A extends null {
  constructor() { }  // Would throw a ReferenceError.
}