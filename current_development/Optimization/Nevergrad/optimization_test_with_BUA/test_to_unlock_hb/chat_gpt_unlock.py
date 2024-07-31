class NestedHoneybeeObject:
    def __init__(self):
        self._locked_attribute = 'nested_locked_value'
        self._is_locked = True

    def unlock(self):
        self._is_locked = False

    def lock(self):
        self._is_locked = True

    @property
    def locked_attribute(self):
        if self._is_locked:
            raise AttributeError("Attribute is locked")
        return self._locked_attribute

    @locked_attribute.setter
    def locked_attribute(self, value):
        if self._is_locked:
            raise AttributeError("Attribute is locked")
        self._locked_attribute = value

class HoneybeeObject:
    def __init__(self):
        self._locked_attribute = 'locked_value'
        self._is_locked = True
        self.nested_object = NestedHoneybeeObject()

    def unlock(self):
        self._is_locked = False
        self.nested_object.unlock()  # Unlock nested object

    def lock(self):
        self._is_locked = True
        self.nested_object.lock()  # Lock nested object

    @property
    def locked_attribute(self):
        if self._is_locked:
            raise AttributeError("Attribute is locked")
        return self._locked_attribute

    @locked_attribute.setter
    def locked_attribute(self, value):
        if self._is_locked:
            raise AttributeError("Attribute is locked")
        self._locked_attribute = value

def is_lockable(obj):
    return hasattr(obj, 'unlock') and callable(getattr(obj, 'unlock'))

def is_locked(obj):
    return hasattr(obj, '_is_locked') and getattr(obj, '_is_locked')

def recursive_unlock(obj):
    if is_lockable(obj) and is_locked(obj):
        obj.unlock()

    for attr_name in dir(obj):
        attr_value = getattr(obj, attr_name)
        if is_lockable(attr_value) and is_locked(attr_value):
            recursive_unlock(attr_value)

def recursive_lock(obj):
    if is_lockable(obj):
        obj.lock()

    for attr_name in dir(obj):
        attr_value = getattr(obj, attr_name)
        if is_lockable(attr_value):
            recursive_lock(attr_value)

# Example worker function
def worker(hb_object):
    recursive_unlock(hb_object)
    try:
        # Perform operations on unlocked_hb
        print(hb_object.locked_attribute)  # Access the unlocked attribute
        print(hb_object.nested_object.locked_attribute)  # Access the nested unlocked attribute
        hb_object.locked_attribute = 'new_value'
        hb_object.nested_object.locked_attribute = 'new_nested_value'
    finally:
        recursive_lock(hb_object)
    return hb_object

# Simulate using ProcessPoolExecutor
from concurrent.futures import ProcessPoolExecutor

hb_object = HoneybeeObject()

with ProcessPoolExecutor() as executor:
    future = executor.submit(worker, hb_object)
    result = future.result()

print(result.locked_attribute)  # Should print 'new_value'
print(result.nested_object.locked_attribute)  # Should print 'new_nested_value'
