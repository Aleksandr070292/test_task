from web3 import Web3
import json

# Установим соединение с Ethereum через Infura
infura_url = "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID"
web3 = Web3(Web3.HTTPProvider(infura_url))

# Адреса контрактов Uniswap V2 Factory и ERC20 ABI
factory_address = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
factory_abi = json.loads('[...]')  # Вставьте ABI для Uniswap V2 Factory
erc20_abi = json.loads('[...]')  # Вставьте ABI для ERC20 токена

# Функция для получения адреса пула
def get_pool_address(token0, token1):
    pair_hash = web3.keccak(text="UniswapV2Pair").hex()
    salt = web3.solidityKeccak(['address', 'address'], sorted([token0, token1]))
    pool_address = web3.solidityKeccak(['bytes', 'address', 'bytes'], ['\xff', factory_address, salt]).hex()
    return web3.toChecksumAddress(pool_address[12:])

# Получим цену токена из пула
def get_token_price(pool_address, token0, token1):
    contract = web3.eth.contract(address=pool_address, abi=erc20_abi)
    reserves = contract.functions.getReserves().call()
    reserve0 = reserves[0]
    reserve1 = reserves[1]
    if token0.lower() < token1.lower():
        return reserve1 / reserve0
    else:
        return reserve0 / reserve1

def main():
    # Установите адреса токенов
    token0 = web3.toChecksumAddress("0x...")  # Адрес первого токена (например, ETH)
    token1 = web3.toChecksumAddress("0x...")  # Адрес второго токена (например, USDT)
    
    # Получаем адреса пулов и цены
    pools = [get_pool_address(token0, token1) for _ in range(2)]
    prices = [get_token_price(pool, token0, token1) for pool in pools]

    for i, pool in enumerate(pools):
        print(f"Адрес пула {i+1}: {pool}")
        print(f"Цена токена на пуле {i+1}: {prices[i]}")

    # Расчет разницы в цене
    price_difference = abs(prices[0] - prices[1]) / max(prices[0], prices[1]) * 100
    print(f"Разница в цене: {price_difference:.2f}%")

    # Проверка на арбитражную возможность
    if price_difference > 0.5:
        print("Возможна арбитражная возможность!")

if __name__ == "__main__":
    main()