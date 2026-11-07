from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel

app = FastAPI(title='MY API')

next_id = 0
user_list = []
category_list = []
product_list = []
order_list = []
order_items_list = []


logined = None

class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None

class CategoryUpdate(BaseModel):
    name: str

class ProductUpdate(BaseModel):
    title: str | None = None
    price: int | None = None
    category_id: int | None = None

class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


@app.get('/users')
def get_users():
    return user_list

@app.post('/create')
def register(username: str, password: str):
    global next_id
    next_id += 1
    user = {
        'id': next_id,
        'username': username,
        'password': password
    }
    user_list.append(user)
    return user

@app.post('/login')
def login(username: str, password: str):
    global logined
    for u in user_list:
        if u['username'] == username and u['password'] == password:
            logined = u
            return {"message": "Login successful", "user_id": u['id']}

    return {"error": "Invalid username or password"}

@app.post('/logout')
def logout():
    global logined
    logined = None
    return {'mesagge': 'logout succesfully'}

@app.post('/add-catagory')
def add_category(name: str):
    global logined, next_id
    if logined:
        next_id += 1
        category = {
            'id': next_id,
            'name': name
        }
        category_list.append(category)
        return category
    if not logined:
        return {'error': 'you must be logined'}

@app.delete('/delete')
def delete(id: int):
    if logined:
        for c in category_list:
            if c['id'] == id:
                category_list.remove(c)
                return {"message": f"Category with id {id} deleted successfully"}
        return {"error": "Category not found"}
    return {'error': 'you must be logined'}


@app.post('/add-product')
def add_product(category_id: int, title: str, description: str, price: int):
    global next_id
    next_id += 1
    product = {
        'id': next_id,
        'category_id': category_id,
        'title': title,
        'description': description,
        'price': price
    }
    product_list.append(product)
    return product

@app.post('/add-order')
def add_order(user_id: int, product_id: int, status: str):
    global next_id
    next_id += 1
    order = {
        'id': next_id,
        'user_id': user_id,
        'product_id': product_id,
        'status': status
    }
    order_list.append(order)
    return order


# ==================== 15 API ЗАДАНИЙ ====================

# 1. GET /users/{user_id}
@app.get('/users/{user_id}')
def get_user(user_id: int = Path(..., ge=1)):
    for u in user_list:
        if u['id'] == user_id:
            return {
                'id': u['id'],
                'username': u['username']
            }
    raise HTTPException(status_code=404, detail="User not found")

# 2. PATCH /users/{user_id}
@app.patch('/users/{user_id}')
def update_user(data: UserUpdate, user_id: int = Path(..., ge=1)):
    for u in user_list:
        if u['id'] == user_id:
            if data.username is not None:
                for other in user_list:
                    if other['username'] == data.username and other['id'] != user_id:
                        raise HTTPException(status_code=400, detail="Username already exists")
                u['username'] = data.username
            if data.password is not None:
                u['password'] = data.password
            return {
                'id': u['id'],
                'username': u['username']
            }
    raise HTTPException(status_code=404, detail="User not found")

# 3. DELETE /users/{user_id}
@app.delete('/users/{user_id}')
def delete_user(user_id: int = Path(..., ge=1)):
    for o in order_list:
        if o['user_id'] == user_id:
            raise HTTPException(status_code=400, detail="Cannot delete user with orders")
    for u in user_list:
        if u['id'] == user_id:
            user_list.remove(u)
            return {"message": f"User with id {user_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="User not found")


# 4. GET /categories/{category_id}
@app.get('/categories/{category_id}')
def get_category(category_id: int = Path(..., ge=1)):
    for c in category_list:
        if c['id'] == category_id:
            return c
    raise HTTPException(status_code=404, detail="Category not found")

# 5. PUT /categories/{category_id}
@app.put('/categories/{category_id}')
def update_category(data: CategoryUpdate, category_id: int = Path(..., ge=1)):
    if not data.name.strip():
        raise HTTPException(status_code=400, detail="Category name cannot be empty")
    for c in category_list:
        if c['id'] == category_id:
            c['name'] = data.name
            return c
    raise HTTPException(status_code=404, detail="Category not found")

# 6. DELETE /categories/{category_id}
@app.delete('/categories/{category_id}')
def delete_category(category_id: int = Path(..., ge=1)):
    for p in product_list:
        if p.get('category_id') == category_id:
            raise HTTPException(status_code=400, detail="Cannot delete category with products")
    for c in category_list:
        if c['id'] == category_id:
            category_list.remove(c)
            return {"message": f"Category with id {category_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="Category not found")

# 7. GET /categories/{category_id}/products
@app.get('/categories/{category_id}/products')
def get_category_products(category_id: int = Path(..., ge=1)):
    category_exists = False
    for c in category_list:
        if c['id'] == category_id:
            category_exists = True
            break
    if not category_exists:
        raise HTTPException(status_code=404, detail="Category not found")

    result = []
    for p in product_list:
        if p.get('category_id') == category_id:
            result.append(p)
    return result


# 11. GET /products/search?title=iphone (объявлен ПЕРЕД /products/{product_id})
@app.get('/products/search')
def search_products(title: str = Query(..., min_length=1)):
    result = []
    for p in product_list:
        if title.lower() in p['title'].lower():
            result.append(p)
    return result

# 12. GET /products/filter?min_price=500&max_price=2000 (объявлен ПЕРЕД /products/{product_id})
@app.get('/products/filter')
def filter_products(
    min_price: int | None = Query(default=None, ge=0),
    max_price: int | None = Query(default=None, ge=0)
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")

    result = []
    for p in product_list:
        if min_price is not None and p['price'] < min_price:
            continue
        if max_price is not None and p['price'] > max_price:
            continue
        result.append(p)
    return result

# 8. GET /products/{product_id}
@app.get('/products/{product_id}')
def get_product(product_id: int = Path(..., ge=1)):
    for p in product_list:
        if p['id'] == product_id:
            category_name = None
            for c in category_list:
                if c['id'] == p.get('category_id'):
                    category_name = c['name']
                    break
            return {
                'id': p['id'],
                'title': p['title'],
                'description': p.get('description'),
                'price': p['price'],
                'category_id': p.get('category_id'),
                'category_name': category_name
            }
    raise HTTPException(status_code=404, detail="Product not found")

# 9. PATCH /products/{product_id}
@app.patch('/products/{product_id}')
def update_product(data: ProductUpdate, product_id: int = Path(..., ge=1)):
    for p in product_list:
        if p['id'] == product_id:
            if data.price is not None:
                if data.price <= 0:
                    raise HTTPException(status_code=400, detail="Price must be positive")
                p['price'] = data.price
            if data.category_id is not None:
                cat_exists = False
                for c in category_list:
                    if c['id'] == data.category_id:
                        cat_exists = True
                        break
                if not cat_exists:
                    raise HTTPException(status_code=404, detail="Category not found")
                p['category_id'] = data.category_id
            if data.title is not None:
                p['title'] = data.title
            return p
    raise HTTPException(status_code=404, detail="Product not found")

# 10. DELETE /products/{product_id}
@app.delete('/products/{product_id}')
def delete_product(product_id: int = Path(..., ge=1)):
    for item in order_items_list:
        if item['product_id'] == product_id:
            raise HTTPException(status_code=400, detail="Cannot delete product that is in orders")
    for o in order_list:
        if o.get('product_id') == product_id:
            raise HTTPException(status_code=400, detail="Cannot delete product that is in orders")
    for p in product_list:
        if p['id'] == product_id:
            product_list.remove(p)
            return {"message": f"Product with id {product_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="Product not found")


# 13. GET /orders/{order_id}
@app.get('/orders/{order_id}')
def get_order(order_id: int = Path(..., ge=1)):
    for o in order_list:
        if o['id'] == order_id:
            items = []
            for item in order_items_list:
                if item['order_id'] == order_id:
                    product_info = None
                    for p in product_list:
                        if p['id'] == item['product_id']:
                            product_info = p
                            break
                    items.append({
                        'id': item['id'],
                        'product_id': item['product_id'],
                        'quantity': item['quantity'],
                        'price': item['price'],
                        'product': product_info
                    })
            return {
                'id': o['id'],
                'user_id': o['user_id'],
                'status': o['status'],
                'items': items
            }
    raise HTTPException(status_code=404, detail="Order not found")

# 14. POST /orders/{order_id}/items
@app.post('/orders/{order_id}/items')
def add_order_item(data: OrderItemCreate, order_id: int = Path(..., ge=1)):
    global next_id
    if data.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0")

    order_exists = False
    for o in order_list:
        if o['id'] == order_id:
            order_exists = True
            break
    if not order_exists:
        raise HTTPException(status_code=404, detail="Order not found")

    product = None
    for p in product_list:
        if p['id'] == data.product_id:
            product = p
            break
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for item in order_items_list:
        if item['order_id'] == order_id and item['product_id'] == data.product_id:
            item['quantity'] += data.quantity
            return item

    next_id += 1
    new_item = {
        'id': next_id,
        'order_id': order_id,
        'product_id': data.product_id,
        'quantity': data.quantity,
        'price': product['price']
    }
    order_items_list.append(new_item)
    return new_item

# 15. GET /orders/{order_id}/total
@app.get('/orders/{order_id}/total')
def get_order_total(order_id: int = Path(..., ge=1)):
    order_exists = False
    for o in order_list:
        if o['id'] == order_id:
            order_exists = True
            break
    if not order_exists:
        raise HTTPException(status_code=404, detail="Order not found")

    total = 0
    for item in order_items_list:
        if item['order_id'] == order_id:
            total += item['price'] * item['quantity']

    return {'order_id': order_id, 'total': total}
