from blockchain import suspend_batch_on_chain, is_batch_suspended_on_chain, PRIVATE_KEY

print(suspend_batch_on_chain('demo-batch', PRIVATE_KEY))
print(is_batch_suspended_on_chain('demo-batch'))
