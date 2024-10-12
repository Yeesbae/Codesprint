import searoute as sr

#Define origin and destination points:
origin = [14.058324,108.277199]

destination = [1.290270,103.851959]


route = sr.searoute(origin, destination)
# > Returns a GeoJSON LineString Feature
# show route distance with unit
print("{:.1f} {}".format(route.properties['length'], route.properties['units']))