from datetime import date

hgoe = date(2026, 1, 1)
print(hgoe)
print(hgoe.year)
print(hgoe.month)
print(hgoe.day)
print(type(hgoe))
print(hgoe.ctime())
print(hgoe.toordinal())
print(hgoe.isoformat())
print(hgoe.strftime("%Y-%m-%d"))
print(hgoe.strftime("%Y%m%d"))
print(hgoe.strftime("%Y%m%d%H%M%S"))
