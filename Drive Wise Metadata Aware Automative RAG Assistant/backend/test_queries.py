from database.queries import get_all_brands, get_cars_by_brand


print("\n=== BRANDS ===")

brands = get_all_brands()

for brand in brands:
    print(brand)


print("\n=== CARS ===")

if brands:
    first_brand_id = brands[0]["id"]

    cars = get_cars_by_brand(first_brand_id)

    for car in cars:
        print(car)