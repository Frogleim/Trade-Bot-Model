from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import zipfile
import os
from pydantic import BaseModel
import db
import json
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
origins = [
    "http://77.37.51.134:8000",  # Your frontend server origin
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Database(BaseModel):
    table_name: str


class BinanceKeys(BaseModel):
    api_key: str
    api_secret: str


class TradesCoins(BaseModel):
    symbol: str
    quantity: int
    checkpoints: list
    stop_loss: float
    indicator: str


class UpdateTradeCoins(BaseModel):
    column: str
    value: str
    indicator: str


class Signal(BaseModel):
    symbol: str
    signal: str
    entry_price: float
    indicator: str


base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, r"Trade-Bot/coins_trade/logs")
sys_log_file_path = os.path.join(files_dir, "system_logs.log")
error_log_file_path = os.path.join(files_dir, "error_logs.log")
action_log_file_path = os.path.join(files_dir, "actions.log")


@app.get("/get-sys-log")
async def get_log():
    # Check if the log file exists
    if os.path.exists(sys_log_file_path):
        return FileResponse(sys_log_file_path, media_type='application/octet-stream', filename='system_log.logs')
    else:
        raise HTTPException(status_code=404, detail="Log file not found")


@app.get("/get-error-log")
async def get_error_log():
    # Check if the log file exists
    if os.path.exists(error_log_file_path):
        return FileResponse(error_log_file_path, media_type='application/octet-stream', filename='error_log.logs')
    else:
        raise HTTPException(status_code=404, detail="Log file not found")


@app.post('/insert-signal')
def insert_signal(signal_data: Signal):
    my_db = db.DataBase()
    my_db.clean_db(table_name='signal')
    symbol = signal_data.symbol
    signal = signal_data.signal
    entry_price = signal_data.entry_price
    indicator = signal_data.indicator
    try:

        my_db = db.DataBase()
        my_db.insert_signal(
            symbol=symbol,
            signal=signal,
            entry_price=entry_price,
            indicator=indicator
        )
        return {"Message": "Success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f'Failed to insert signal\nError message: {e}')


@app.get("/get-action-log")
async def get_action_log():
    # Check if the log file exists
    if os.path.exists(action_log_file_path):
        return FileResponse(action_log_file_path, media_type='application/octet-stream', filename='actions_log.logs')
    else:
        raise HTTPException(status_code=404, detail="Log file not found")


@app.post('/set_credentials/')
def set_credentials(keys: BinanceKeys):
    api_key = keys.api_key
    api_secret = keys.api_secret
    my_db = db.DataBase()
    my_db.insert_binance_keys(api_key=api_key, api_secret=api_secret)
    return {"Message": "API keys insert successfully"}


@app.post('/set_trade_coins/')
def trades_coins(trade_coin: TradesCoins):
    symbol = trade_coin.symbol
    quantity = trade_coin.quantity
    checkpoints = trade_coin.checkpoints
    stop_loss = trade_coin.stop_loss
    indicator = trade_coin.indicator
    try:
        my_db = db.DataBase()
        my_db.insert_trades_coins(
            symbol=symbol,
            quantity=quantity,
            checkpoints=checkpoints,
            stop_loss=stop_loss,
            indicator=indicator
        )
        return {
            "Message": "Success",
            "Data": {
                "Symbol": symbol,
                "quantity": quantity,
                "checkpoints": checkpoints,
                "stop_loss": stop_loss,
                "indicator": indicator
            }

        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error while inserting settings for indicator {indicator}")


@app.post("/update_settings/")
def update_settings(updated: UpdateTradeCoins):
    column = updated.column
    value = updated.value
    indicator = updated.indicator
    try:
        my_db = db.DataBase()
        my_db.update_trade_coins(
            column=column,
            update_value=value,
            indicator=indicator
        )
        return {'Message': "Success"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f'Error while updating column: {column}')


@app.get('/get_trade_setting/')
def get_trade_coins():
    my_db = db.DataBase()
    data = my_db.get_trade_settings()
    transformed_data = [
        {
            "id": item[0],
            "symbol": item[1],
            "value": item[2],
            "ratios": item[3],
            "decimal_value": float(item[4]),
            "indicator": item[5]
        }
        for item in data
    ]
    json_data = json.dumps(transformed_data, indent=4)
    return json.loads(json_data)


@app.get('/is_finished')
def is_finished():
    try:
        my_db = db.DataBase()
        finished = my_db.check_is_finished()
        if finished:
            return {'Message': True}
        else:
            return {'Message': False}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Error getting trade status\nMessage: {e}')


@app.get('/get_trades_history/')
def get_trade_coins():
    my_db = db.DataBase()
    data = my_db.get_trade_history()
    try:
        transformed_data = [
            {
                "id": item[0],
                "symbol": item[1],
                "entry_price": item[2],
                "exit_price": item[3],
                "profit": float(item[4]),
                "is_profit": item[5],
                "indicator": item[-1]
            }
            for item in data
        ]
        json_data = json.dumps(transformed_data, indent=4)
        return json.loads(json_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail='Something wrong!')


@app.get("/clean_history/")
def app_clean_history():
    try:
        my_db = db.DataBase()
        my_db.clean_db(table_name='trades_history')
        return {"Message": "Trades history cleaned successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to clean trades history")


@app.post('/clean_db/')
def clean_table(table: Database):
    try:
        my_db = db.DataBase()
        my_db.clean_db(table_name=table.table_name)
        return {'Message': f'Successfully cleaned {table.table_name}'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to clean {table.table_name}')
#
#
# if __name__ == "__main__":
#     import uvicorn
#
#     uvicorn.run(app, host="0.0.0.0", port=8000)
