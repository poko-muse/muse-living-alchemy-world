def daily_economy(rng, economy, residents):
    """Simple production/consumption. Never negative stock/funds. Returns events list."""
    events=[]
    for shop in economy.get("shops", []):
        for item in shop.get("inventory", []):
            # consumption 0-2, production 0-2 depending on rng
            consumed = rng.randint(0,2)
            produced = rng.randint(0,2)
            delta = produced - consumed
            new_stock = max(0, item["stock"] + delta)
            actual_delta = new_stock - item["stock"]
            item["stock"] = new_stock
            if actual_delta!=0:
                events.append(f"{shop['name']}: {item['material_id']} 在庫 {actual_delta:+d} -> {new_stock}")
            # price micro-adjustment, floor 1
            if consumed>produced:
                item["price"] = item["price"]+1
            elif produced>consumed and item["price"]>1:
                item["price"] = item["price"]-1
    return events
