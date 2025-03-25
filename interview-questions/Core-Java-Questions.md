

### Core Java Questions

#### **Explain OOPS Concept ?**
  - **Encapsulation**
    - Is the mechanism that binds together code and the data it manipulates,  and keeps both safe from outside interference/misuse
    - Is a protective wrapper that prevents the code and data from being arbitrarily accessed by other code defined outside the wrapper
    - Access to the code and data inside the wrapper is tightly controlled through a well-defined interface
    - The public interface of a class represents access to the external users of the class. The private methods and data can only be accessed by code that is a member of the class
  - **Inheritance**
    - Is a mechanism in which one object acquires all the properties and behaviors of a parent object.
    - Supports the concept of hierarchical classification
    - Inheritance interacts with encapsulation. If a given class encapsulates some attributes, then any subclass will have the same attributes plus any that it adds as part of its specialization
    - Code reusability
  - **Polymorphism**
    - Is the ability of an object to take many forms
    - It describes the concept that you can access objects of different types through the same interface. Each type can provide its own independent implementation of this interface.
    - Can perform a single task in different ways. In the technical world, polymorphism allows one to do multiple implementations by defining one interface.
    - Types of polymorphism
      - compile time polymorphism ( method overloading )
        - methods in the same class have the same name but different parameters
      - runtime polymorphism ( method overriding )
        - method signature (name and parameters) are the same in the superclass and the child class
  - **Abstraction**
    - Is the process of hiding certain details and showing only essential information to the user
    - Implemented in java using abstract class & interfaces

#### **What is Association, aggregation, and composition in OOP's ?**

#### **Explain working/usage of HashMap ?**

#### **Explain working/usage of ConcurrentHashMap ?**

#### **Explain comparator & comparable interfaces, what's usage of them ?**
  - **Comparator**
    - The Comparator provides multiple sorting sequences. In other words, we can sort the collection on the basis of multiple elements such as id, name, and price etc.
    - Comparator doesn't affect the original class, i.e., the actual class is not modified.
    - Comparator provides compare() method to sort elements
    - A Comparator is present in the java.util package.
    - We can sort the list elements of Comparator type by Collections.sort(List, Comparator) method.
  - **Comparable**
    - Comparable provides a single sorting sequence. In other words, we can sort the collection on the basis of a single element such as id, name, and price
    - Comparable affects the original class, i.e., the actual class is modified
    - Comparable provides **compareTo(T obj)** method to sort elements
    - Comparable is present in java.lang package
    - Arrays.sort(x) and Collection.sort(x) uses compareTo() method of Comparable class

#### **Why String is Immutable/Final in Java ?**

#### **What is the default method, and why is it required ?**
  - Method in the interface that has a predefined body is known as the default method
  - Concept of default method is introduced in java 8 to add the new methods in the existing interfaces in such a way so that they are backward compatible

#### **What is lambda expression ?**
  - Lambda expressions let you express instances of single-method classes more compactly
  - A lambda expression is a short block of code which takes in parameters and returns a value

#### **Explain Streams working ?**

#### **Why do we need to override equals and hashcode methods in Java?**
  - If two objects are equal, then they must have the same hashcode. If two objects have the same hashcode then they may or may not be equal
  - Equals contract
    - **Reflexive:** For any non-null reference value x, x.equals(x) should return true
    - **Symmetric:** For any non-null reference values x and y, x.equals(y) should return true if and only if y.equals(x) returns true.
    - **Transitive:** For any non-null reference values x, y, and z, if x.equals(y) returns true and y.equals(z) returns true, then x.equals(z) should return true
    - **Consistent:** Multiple invocations of x.equals(y) consistently return true or consistently return false. The value of equals() should change only if a property that is contained in equals() changes
  - HashCode Contract
    - **Internal consistency:** the value of hashCode() may only change if a property that is in equals() changes
    - **Equals consistency:** objects that are equal to each other must return the same hashCode
    - **Collisions:** unequal objects may have the same hashCode

#### **Explain java.utils package ?**

#### **Have you used functional interfaces, explain the use case ?**

#### **There is list of employee, calculate the sum of salary of employees of specific dept/grade with service greater than 5 years. How you will do using Streams ?**

#### **Explain limit vs skip methods in streams ?**

#### **Which new JDK features in 11/17 ?**

#### **Explain sorting algorithms used in JDK, explain the best sorting algorithm in Java ?**
