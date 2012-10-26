boo = 0.0

def booaddition():
    boo = 1.0
    print('from within booaddition')
    print boo

def anotherfunction():
    print boo

print('before booaddition:')
print boo

booaddition()

print('after booaddition:')
print boo

print('from anotherfunction:')
anotherfunction()
