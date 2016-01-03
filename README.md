# phylter

[![Build Status](https://travis-ci.org/ercpe/phylter.svg?branch=master)](https://travis-ci.org/ercpe/phylter) [![Coverage Status](https://coveralls.io/repos/ercpe/phylter/badge.svg?branch=master&service=github)](https://coveralls.io/github/ercpe/phylter?branch=master)


phylter is a mini-dsl filter language. You can use it to allow users to write there own filters without letting them access your database directly (and thus, need to understand your database layout).


## Language

The language implements the following operators: `==` (equals), `>` (greater than), `<` (less than), `>=` (greater than or equals), `<=` (less than or equals) and the two operators `and` and `or`.

The precende of the `and` and `or` operator follows the [python operator precedence](https://docs.python.org/3/reference/expressions.html#operator-precedence).


## Basic usage


    from phylter import parser
    
    parser = parser.Parser()
    query = parser.parse("foo == 'bar'")
    
    query.apply(data)

The query is passed as string to a `Parser` instance which builds a `Query` object. The `apply` method applies the query to the passed iterable using the most appropiate backend (see below).


## Backends

The `Query`'s `apply` method decides the best backend to use based on the type of the passed iterable. As a fallback, the `ObjectsBackend` will be used.

The most universal backend is the `ObjectsBackend`. This backend applies the query to standard python objects.

The `DjangoBackend` will be used if the `iterable` argument of the `apply` method is a Django `QuerySet` or `Manager` instance. The `DjangoBackend` translates the `Query` object into a Django database query:

	class Person(models.Model):
		first_name = models.CharField(...)
		last_name = models.CharField(...)
		age = models.PositiveIntegerField(...)

	query = Parser().parse("first_name == 'Alice')   
    query.apply(Person.objects)
    
will result in a Django query roughly equivalent to

	Person.objects.filter(first_name='Alice')

and a query like `first_name == 'Bob' or age > 20` in

	Person.objects.filter(Q(first_name='Bob') | Q(age__gt=20))


## License

See LICENSE.txt
