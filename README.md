# BiLira-Algo-Challenge-FTX-Api
BiLira's Algo Challenge, creating and posting market and limit orders through python api

I had to change FTX's class that they provide at https://github.com/ftexchange/ftx/tree/master/rest. I could not install ciso8601 to my Windows machine and also the file did not have any market_order functionality that I could use. I found a way to do so from trial and error and added market_order function that you can check.

Check BiLira Algo Trader Challenge_.pdf for the task itself.
TL-DR: I was to post market and limit orders. First twist was that market orders should have a calculated final cost because of the market not being %100 efficient at providing takers. Second twist was that limit orders have an underlying iceberg parameter that divides the whole order into eg:4 different orders so that it isn't immediately visible as a decently sized limit order.
