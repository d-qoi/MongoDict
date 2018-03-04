# MongoDict
Python Dictionary backed by a MongoDB collection, using Pymongo as the main connection.

---


## How to use!

	
```python
MongoDict(collection=None, mirror=True, write_back=True, warm_cache=False)
```

* collection: 
   A pointer to the collection to use :: client[database][collection]

* mirror: 
When set to `True`, it will pull Everything from the collection (when requested) and set it in a dictionary, this may make lookups faster as it will not pull from the collection for every get.
If the database is updated behind the cache, it will not be updated locally unless `update_from_db` is called

* write_back: When set to false, it will not write to the database

* warm_cache: When this is true, it will pull everything immediately

Setting Mirrored true and write_back to false will make this behave like a regular dictionary

###Extra functions:
* update_from_db():
This will pull from the database, and update every key in the internal dict. **It will not remove any keys from the internal dictionary**

---
## Notes
The MongoDB backend can only accept so many types (`str`, `int`, `float`, `list`, `set`, `dict`, `tuple`, `datetime`, to name a few, so don't try to do anything extreme with the database, like using it as a jump table with function pointers, unless write_back is set to false.
The Internal variable `idb` can be accessed directly, and it is a `collections.defaultdict`, which can be used like any other database, if the needs come around.

Some of the functionality may be a bit weird, considering that MongoDB returns None instead of throwing an exception for failed finds (at least I am not checking for failed finds) so this may not throw key exceptions.