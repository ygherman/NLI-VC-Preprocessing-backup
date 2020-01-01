import pprint

from VC_collections.Collection import Collection

collection = Collection('Alma', 'Architect', 'POrWe')


types= [type(getattr(collection, name)).__name__ for  name in dir(collection) if name[:2] != '__' and name[-2:] != '__']
names = [getattr(collection, name) for  name in dir(collection) if name[:2] != '__' and name[-2:] != '__']

pprint.pprint(dict(zip(names, types)))