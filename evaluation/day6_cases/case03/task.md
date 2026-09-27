# Dispatch a Packed Shipment

Dispatch a packed shipment whose units have already been reserved in inventory.
Mark it shipped, subtract its quantity from both on-hand and reserved units, and
record the tracking reference. Reject an empty tracking reference or insufficient
on-hand stock without changing either record. Dispatching a shipped shipment again
must not deduct inventory a second time.
