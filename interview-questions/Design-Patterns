# Java Design Patterns

## 1. Creational Patterns
_Deal with object creation mechanisms_

### Singleton
- Ensures only one instance of a class exists
- Provides global access point to the instance
- Common uses: Logger, Configuration, Database connections
- Implementation types: Eager, Lazy, Thread-safe, Double-checked locking

### Factory Method
- Defines interface for creating objects
- Lets subclasses decide which class to instantiate
- Promotes loose coupling
- Example: `Calendar.getInstance()`

### Abstract Factory
- Creates families of related objects
- Higher level than Factory Method
- Useful when system needs multiple product families

### Builder
- Separates complex object construction from representation
- Allows step-by-step construction
- Example: `StringBuilder`

### Prototype
- Creates new objects by cloning prototypes
- Avoids costly creation process
- Requires implementing `Cloneable` interface

## 2. Structural Patterns
_Concerned with class and object composition_

### Adapter
- Bridges incompatible interfaces
- Wraps an existing class
- Example: Arrays.asList()

### Decorator
- Adds responsibilities dynamically
- Alternative to subclassing
- Example: Java I/O streams

### Facade
- Provides simplified interface to complex subsystem
- Reduces subsystem dependencies
- Typical in library design

### Composite
- Treats individual and composite objects uniformly
- Builds tree structures
- Example: GUI components

### Proxy
- Controls access to another object
- Types: Virtual, Remote, Protection, Smart reference
- Example: `java.lang.reflect.Proxy`

## 3. Behavioral Patterns
_Deal with object interaction and responsibility distribution_

### Observer
- One-to-many dependency between objects
- Publisher-Subscriber pattern
- Example: Event listeners in Swing

### Strategy
- Defines family of algorithms
- Makes them interchangeable
- Example: `Comparator` interface

### Command
- Encapsulates request as object
- Supports undoable operations
- Example: Runnable interface

### Iterator
- Provides way to access elements sequentially
- Hides underlying implementation
- Example: `java.util.Iterator`

### Template Method
- Defines algorithm skeleton
- Lets subclasses redefine certain steps
- Example: `HttpServlet` class

### State
- Allows object to alter behavior when state changes
- State-specific behavior in separate classes
- Alternative to large conditionals
