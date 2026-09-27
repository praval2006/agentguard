# Start a Work Order

Let a technician start a queued work order. Starting it moves it to in_progress
and retains its description. Starting an already in-progress order is harmless.
A completed order cannot be started again; reject that request without changing it.
