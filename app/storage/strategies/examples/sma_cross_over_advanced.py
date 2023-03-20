from components import Parameter
from components import Strategy, on_step
from components.orders.order import Order, LimitOrder, StopOrder
from components.orders.position import Position
from components.strategy import ta
from components.strategy.decorators import after
from components.strategy.strategy import Plot


class SMACrossOverAdvanced(Strategy):
    sma_fast_length = Parameter(10)
    sma_slow_length = Parameter(100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        all_close = self.data.all('close')
        self.sma_fast = ta.sma(all_close, int(self.sma_fast_length))
        self.sma_slow = ta.sma(all_close, int(self.sma_slow_length))

    @on_step
    def check_for_crossover(self):
        # add logic to crossover here
        cross_over = ta.logic.crossover(self.sma_fast, self.sma_slow)
        if cross_over:
            open_order = Order(
                type='market',
                side='buy',
                qty=100,
                symbol=self.symbol.symbol,
                filled_avg_price=self.data.close,
                timestamp=self.data.timestamp,
            )
            take_profit = LimitOrder(
                side='sell',
                qty=100,
                symbol=self.symbol.symbol,
                limit_price=self.data.close + 5,
            )
            stop_loss = StopOrder(
                side='sell',
                qty=100,
                symbol=self.symbol.symbol,
                stop_price=self.data.close - 5,
            )
            p = Position(orders=[open_order, take_profit, stop_loss])
            self.positions.append(p)

    @after
    def create_plots(self):
        self.export_plots([
            Plot(self.sma_fast, name='sma_fast'),
            Plot(self.sma_slow, name='sma_slow'),
        ])

