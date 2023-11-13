#!/usr/bin/env python

import asyncio
import itertools
import json
import websockets

from connect4 import PLAYER1, PLAYER2, Connect4

def print_info( websocket ) :
    tmp1 = hasattr( websocket, 'ConnectionClosed' )
    tmp2 = hasattr( websocket, 'ConnectionClosedError' )
    tmp3 = hasattr( websocket, 'ConnectionClosedOK' );
    var1 = 'x';
    var2 = 'x';
    var3 = 'x';
    if( tmp1 ) : var1 = websocket.ConnectionClosed;
    if( tmp2 ) : var2 = websocket.ConnectionClosedError;
    if( tmp3 ) : var3 = websocket.ConnectionClosedOK;

    print( websocket.id, var1, var2, var3 );



async def handler(websocket):
    # Initialize a Connect Four game.
    print_info( websocket );
    game = Connect4()
    # Players take alternate turns, using the same browser.
    turns = itertools.cycle([PLAYER1, PLAYER2])
    player = next(turns)

    async for message in websocket:
        print( str(websocket.id) + ' : [' + message + ']' )
        # Parse a "play" event from the UI.
        event = json.loads(message) #json.decoder.JSONDecodeError:
        assert event["type"] == "play"
        column = event["column"]
        try:
            # Play the move.
            row = game.play(player, column)
        except RuntimeError as exc:
            # Send an "error" event if the move was illegal.
            event = {
                "type": "error",
                "message": str(exc),
            }
            print( 'error', json.dumps(event) )
            await websocket.send(json.dumps(event))
            continue
        # Send a "play" event to update the UI.
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        await websocket.send(json.dumps(event))
        # If move is winning, send a "win" event.
        if game.winner is not None:
            event = {
                "type": "win",
                "player": game.winner,
            }
            await websocket.send(json.dumps(event))
        # Alternate turns.
        player = next(turns)

'''
async def handler(websocket):
    for player, column, row in [
        (PLAYER1, 3, 0),
        (PLAYER2, 3, 1),
        (PLAYER1, 4, 0),
        (PLAYER2, 4, 1),
        (PLAYER1, 2, 0),
        (PLAYER2, 1, 0),
        (PLAYER1, 5, 0),
    ]:
        event = {
            "type": "play",
            "player": player,
            "column": column,
            "row": row,
        }
        await websocket.send(json.dumps(event))
        await asyncio.sleep(0.5)
    event = {
        "type": "win",
        "player": PLAYER1,
    }
    await websocket.send(json.dumps(event))



async def handler(websocket):
    while True:
        try:
            message = await websocket.recv()
        except websockets.ConnectionClosedOK:
            break
        print(message)
'''

async def main():
    print( 'wait for ws://localhost:8001' )
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())


# $ python -m http.server