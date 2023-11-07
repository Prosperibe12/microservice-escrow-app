from escrow_app import models

# compute product amount from list of products
def compute_total_amount(products):
    '''Compute Total amount for transaction products'''
    prices = [each['price'] for each in products]
    return sum(prices)

# calculate escrow amount fee
def compute_escrow_transaction_fee(products):
    '''
    Function that computes escrow service charge.
    Fomula:
    (if product_amount > 10,000,000 // 1%)
    (if product_amount > 1,000,000 and < 10,000,000 // 0.5%)
    (if product_amount < 1,000,000 // 0.1%)
    '''
    product_amount = compute_total_amount(products)
    if product_amount > 10000000.00:
        fee = product_amount*0.01
    if (product_amount >= 1000000.00) and (product_amount < 10000000.00):
        fee = product_amount*0.005
    if product_amount < 1000000.00:
        fee = product_amount*0.001
    return fee

def product_transaction(data,trans):
    '''This function takes the transaction product and save in a product table'''
    inst = models.Transaction.objects.get(Transaction_id=trans)

    logs = [models.Product(category=d['category'], product_name=d['product_name'],
                            quantity=d['quantity'], price=d['price'], Transaction=inst,
                          )for d in data]
    # use bulk_create to create multiple new log objects
    models.Product.objects.bulk_create(logs)
  
def create_transaction_order(data):
    '''This function creates order when buyer accepts to proceed with the
        transaction terms, order status is set as 'Order Created'.
    '''
    try:
        transaction = models.Transaction.objects.get(Transaction_id=data['Transaction_id'])
    except:
        models.Transaction.DoesNotExist("Object Not Found")
    amount = compute_total_amount(data['product_list'])
    models.Order.objects.create(
        Transaction_details=transaction,
        amount=amount,
        status='Order Created'
    )