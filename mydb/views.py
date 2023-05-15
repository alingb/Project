import json

from django.shortcuts import render

# Create your views here.

from django.forms import model_to_dict
from mydb.models import ChainDate, TransferDate
from django.http import HttpResponse
from web3 import Web3
from hexbytes import HexBytes
from django.db.models import Q


def getChainMsg(req):
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    chain = ChainDate.objects.last()
    if not chain:
        number = 0
    else:
        number = chain.number
    num = w3.eth.get_block('latest').number
    if int(number) < int(num):
        for c in range(int(number)+1, int(num)):
            chainMsg = w3.eth.get_block(c)
            chain = ChainDate()
            chain.baseFeePerGas = chainMsg["baseFeePerGas"]
            chain.difficulty = chainMsg["difficulty"]
            chain.extraData = chainMsg["extraData"].hex()
            chain.gasLimit = chainMsg["gasLimit"]
            chain.gasUsed = chainMsg["gasUsed"]
            chain.hash = chainMsg["hash"].hex()
            chain.logsBloom = chainMsg["logsBloom"].hex()
            chain.miner = chainMsg["miner"]
            chain.mixHash = chainMsg["mixHash"].hex()
            chain.nonce = chainMsg["nonce"].hex()
            chain.number = chainMsg["number"]
            chain.parentHash = chainMsg["parentHash"].hex()
            chain.receiptsRoot = chainMsg["receiptsRoot"].hex()
            chain.sha3Uncles = chainMsg["sha3Uncles"].hex()
            chain.size = chainMsg["size"]
            chain.stateRoot = chainMsg["stateRoot"].hex()
            chain.timestamp = chainMsg["timestamp"]
            chain.totalDifficulty = chainMsg["totalDifficulty"]
            trs = chainMsg["transactions"]
            chain.transactions = trs
            chain.transactionsRoot = chainMsg["transactionsRoot"].hex()
            chain.uncles = chainMsg["uncles"]
            chain.save()
            if trs:
                for tran in trs:
                    tof = TransferDate.objects.filter(transactionHash=tran.hex())
                    if not tof:
                        w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
                        trs = w3.eth.get_transaction_receipt(tran)
                        num = trs["blockNumber"]
                        tr = w3.eth.get_transaction(tran)
                        value = tr["value"]
                        timestamp = w3.eth.get_block(num).timestamp
                        trans = TransferDate()
                        trans.blockHash = trs["blockHash"].hex()
                        trans.blockNumber = trs["blockNumber"]
                        trans.contractAddress = trs["contractAddress"]
                        trans.cumulativeGasUsed = trs["cumulativeGasUsed"]
                        trans.effectiveGasPrice = trs["effectiveGasPrice"]
                        trans.From = trs["from"]
                        trans.gasUsed = trs["gasUsed"]
                        trans.logs = trs["logs"]
                        trans.logsBloom = trs["logsBloom"].hex()
                        trans.status = trs["status"]
                        trans.to = trs["to"]
                        trans.transactionHash = trs["transactionHash"].hex()
                        trans.transactionIndex = trs["transactionIndex"]
                        trans.type = trs["type"]
                        trans.value = value
                        trans.timestamp = timestamp
                        trans.save()
    return HttpResponse("yes")


def getTransferMsg(req):
    last_num = TransferDate.objects.last()
    if not last_num:
        last_num = 0 
    else:
        last_num = last_num.blockNumber

    chain_data = ChainDate.objects.filter(~Q(transactions=[])).filter(number__lte=last_num).order_by("number").values("transactions")
    for t in chain_data:
        for tran in eval(t["transactions"]):
            tof = TransferDate.objects.filter(transactionHash=tran.hex())
            if not tof:
                w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
                trs = w3.eth.get_transaction_receipt(tran)
                num = trs["blockNumber"]
                tr = w3.eth.get_transaction(tran)
                value = tr["value"]
                timestamp = w3.eth.get_block(num).timestamp
                trans = TransferDate()
                trans.blockHash = trs["blockHash"].hex()
                trans.blockNumber = trs["blockNumber"]
                trans.contractAddress = trs["contractAddress"]
                trans.cumulativeGasUsed = trs["cumulativeGasUsed"]
                trans.effectiveGasPrice = trs["effectiveGasPrice"]
                trans.From = trs["from"]
                trans.gasUsed = trs["gasUsed"]
                trans.logs = trs["logs"]
                trans.logsBloom = trs["logsBloom"].hex()
                trans.status = trs["status"]
                trans.to = trs["to"]
                trans.transactionHash = trs["transactionHash"].hex()
                trans.transactionIndex = trs["transactionIndex"]
                trans.type = trs["type"]
                trans.value = value
                trans.timestamp = timestamp
                trans.save()
    return HttpResponse("yes")


def blockHeightList(req):
    if req.method == "GET":
        fromblock = req.GET.get("fromblock", default="0")
        data_list = []
        if int(fromblock) == 0:
            chain = ChainDate.objects.values("number", "hash", "timestamp", "transactions").order_by("-number")[:15]
            for block in chain:
                number = block["number"]
                hash = block["hash"]
                timestamp = block["timestamp"]
                txs = len(eval(block["transactions"]))
                data_list.append({"number": number,
                                  "hash": hash,
                                  "timestamp": timestamp,
                                  "txs": txs})
        else:
            n = int(fromblock)
            num = ChainDate.objects.last().number
            chain = ChainDate.objects.values("number", "hash", "timestamp", "transactions").order_by("-number")[num-n:num-n+15]
            for block in chain:
                number = block["number"]
                hash = block["hash"]
                timestamp = block["timestamp"]
                txs = len(eval(block["transactions"]))
                data_list.append({"number": number,
                                  "hash": hash,
                                  "timestamp": timestamp,
                                  "txs": txs})
        block_height = {"result": 1, "data": {"data_list": data_list}}
    else:
        block_height = {}
    return HttpResponse(json.dumps(block_height))


def transactionList(req):
    if req.method == "GET":
        fromblock = req.GET.get("fromblock", default=0)
        data_list = []
        if fromblock == 0:
            trans = TransferDate.objects.values("transactionHash", "blockNumber", "timestamp").order_by("-blockNumber")[:15]
            for tran in trans:
                blockNumber = tran["blockNumber"]
                transactionHash = tran["transactionHash"]
                timestamp = tran["timestamp"]
                data_list.append({"blockNumber": blockNumber,
                                  "transactionHash": transactionHash,
                                  "timestamp": timestamp})
        else:
            hash = fromblock
            num = TransferDate.objects.filter(transactionHash=hash).values("id")[0]["id"]
            n = TransferDate.objects.count()
            trans = TransferDate.objects.values("transactionHash", "blockNumber", "timestamp","id").order_by("-id")[n-num+1:n-num+16]
            for tran in trans:
                blockNumber = tran["blockNumber"]
                transactionHash = tran["transactionHash"]
                timestamp = tran["timestamp"]
                data_list.append({"blockNumber": blockNumber,
                                  "transactionHash": transactionHash,
                                  "timestamp": timestamp})
        transaction_list = {"result": 1, "data": {"data_list": data_list}}
    else:
         transaction_list = {}
    return HttpResponse(json.dumps(transaction_list))


def homepageData(req):
    last_chain = ChainDate.objects.last()
    blochHeight = last_chain.number
    number = blochHeight - 100
    blocktimeAvg = (float(last_chain.timestamp) - float(ChainDate.objects.get(number=number).timestamp)) / 100
    totalDifficulty = last_chain.difficulty
    netHashrate = float(totalDifficulty) / float(blocktimeAvg)
    homepage_data = {"result": 1,
                     "data": {"chain_brief": {"blochHeight": blochHeight,
                                              "blocktimeAvg": blocktimeAvg,
                                              "netHashrate": netHashrate,
                                              "totalDifficulty": totalDifficulty}}}
    return HttpResponse(json.dumps(homepage_data))


def addressMsg(req):
    if req.method == "GET":
        address = req.GET.get("address", default="")
        if address:
            w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
            amount_num = w3.eth.get_balance(address)
            amount = float(w3.from_wei(amount_num, "ether"))
            address_msg = {"result": 1,
                           "data": {"data": {"address": address,
                                             "balance": float(amount)}}}
        else:
            address_msg = {"result": 0, "errno": 102, "data": {}}
    else:
        address_msg = {"result": 0, "errno": 102, "data": {}}
    return HttpResponse(json.dumps(address_msg))


def transactionListPage(req):
    if req.method == "GET":
        address = req.GET.get("address", default="")
        if address:
            trans = TransferDate.objects.filter(Q(From=address) | Q(to=address)).order_by("-blockNumber")
            trans_values = trans.values("blockNumber", "transactionHash", "status", "From", "timestamp")
            trans_list = []
            for value in trans_values:
                hash = value["transactionHash"]
                status = value["status"]
                blockHeight = value["blockNumber"]
                if value["From"] == address:
                    type = "OUT"
                else:
                    type = "IN"
                timestamp = value["timestamp"]
                trans_list.append({"timestamp": timestamp,
                                   "type": type,
                                   "blockHeight": blockHeight,
                                   "hash": hash,
                                   "status": status})
            transaction_list = {"result": 1, "data": {"transactions": trans_list}}
        else:
            transaction_list = {"result": 0, "errno": 102, "data": {}}
    else:
        transaction_list = {"result": 0, "errno": 102, "data": {}}
    return HttpResponse(json.dumps(transaction_list))


def detailSearch(req):
    if req.method == "GET":
        keyworld = req.GET.get("keyworld", default="")
        data = {"transactions_data": {}, "address_data": {}, "block_date": {}}
        if keyworld:
            if keyworld.isdigit():
                chain = ChainDate.objects.filter(number=keyworld)
                if chain:
                    chain = chain.values()[0]
                    number = chain["number"]
                    hash = chain["hash"]
                    timestamp = chain["timestamp"]
                    miner = chain["miner"]
                    trs = eval(chain["transactions"])
                    txs = len(trs)
                    transactions = []
                    for tr in trs:
                        trans = TransferDate.objects.filter(transactionHash=tr.hex())
                        if not trans:
                            return HttpResponse(json.dumps({"result": 0, "errno": 102, "data": {}}))
                        trans = trans.values()[0]
                        blockHeight = trans["blockNumber"]
                        timestamp = trans["timestamp"]
                        hash = trans["transactionHash"]
                        status = trans["status"]
                        transactions.append({"blockHeight": blockHeight,
                                             "timestamp": timestamp,
                                             "hash": hash,
                                             "status": status})
                    data.update({"block_date": {"number": number,
                                                "hash": hash,
                                                "timestamp": timestamp,
                                                "miner": miner,
                                                "txs": txs,
                                                "transactions": transactions}})
                else:
                    detail_search = {"result": 0, "errno": 102, "data": {}}
                    return HttpResponse(json.dumps(detail_search))
            elif Web3.is_address(keyworld):
                w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
                amount_num = w3.eth.get_balance(keyworld)
                if not amount_num:
                    detail_search = {"result": 0, "errno": 102, "data": {}}
                    return HttpResponse(json.dumps(detail_search))
                amount = float(Web3.from_wei(amount_num, "ether"))
                data.update({"address_data": {"address": keyworld,
                                              "balance": amount}})
            else:
                trans = TransferDate.objects.filter(transactionHash=keyworld)
                if not trans:
                    detail_search = {"result": 0, "errno": 102, "data": {}}
                    return HttpResponse(json.dumps(detail_search))
                trans = trans.values()[0]
                hash = trans["transactionHash"]
                status = trans["status"]
                blockNumber = trans["blockNumber"]
                timestamp = trans["timestamp"]
                Amount = float(Web3.from_wei(float(trans["value"]), "ether"))
                From = trans["From"]
                to = trans["to"]
                Fees = float(Web3.from_wei(float(float(trans["cumulativeGasUsed"]) * float(trans["effectiveGasPrice"])), 'ether'))
                data.update({"transactions_data": {"hash": hash,
                                                   "status": status,
                                                   "blockBumber": blockNumber,
                                                   "timestamp": timestamp,
                                                   "Amount": Amount,
                                                   "from": From,
                                                   "to": to,
                                                   "Fees": Fees}})
            detail_search = {"result": 1, "data": data}
        else:
            detail_search = {"result": 0, "errno": 102, "data": {}}
    else:
        detail_search = {"result": 0, "errno": 102, "data": {}}
    return HttpResponse(json.dumps(detail_search))


def blockDetail(req):
    if req.method == "GET":
        blockNumber = req.GET.get("block", default="")
        if blockNumber:
            chain = ChainDate.objects.filter(number=blockNumber)
            if not chain:
                return HttpResponse(json.dumps({"result": 0, "errno": 102, "data": {}}))
            chain = chain.values()[0]
            number = chain["number"]
            hash = chain["hash"]
            timestamp = chain["timestamp"]
            miner = chain["miner"]
            trs = eval(chain["transactions"])
            txs = len(trs)
            block_data = {"number": number,
                          "hash": hash,
                          "timestamp": timestamp,
                          "miner": miner,
                          "txs": txs}
            transactions = []
            for tr in trs:
                trans = TransferDate.objects.filter(transactionHash=tr.hex())
                if not trans:
                    return HttpResponse(json.dumps({"result": 0, "errno": 102, "data": {}}))
                trans = trans.values()[0]
                blockHeight = trans["blockNumber"]
                timestamp = trans["timestamp"]
                hash = trans["transactionHash"]
                status = trans["status"]
                transactions.append({"blockHeight": blockHeight,
                                     "timestamp": timestamp,
                                     "hash": hash,
                                     "status": status})
            block_detail = {"result": 1, "data": {"block_data": block_data, "transactions": transactions}}
        else:
            block_detail = {"result": 0, "errno": 102, "data": {}}
    else:
        block_detail = {"result": 0, "errno": 102, "data": {}}
    return HttpResponse(json.dumps(block_detail))


def transactionDetail(req):
    if req.method == "GET":
        hash = req.GET.get("hash", default="")
        if hash:
            trans = TransferDate.objects.filter(transactionHash=hash)
            if not trans:
                return HttpResponse(json.dumps({"result": 0, "errno": 102, "data": {}}))
            trans = trans.values()[0]
            hash = trans["transactionHash"]
            status = trans["status"]
            blockNumber = trans["blockNumber"]
            timestamp = trans["timestamp"]
            value = float(trans["value"])
            Amount = float(Web3.from_wei(value, "ether"))
            From = trans["From"]
            to = trans["to"]
            Fees = float(Web3.from_wei(float(float(trans["cumulativeGasUsed"]) * float(trans["effectiveGasPrice"])), 'ether'))
            transactions = {"transactions_data": {"hash": hash,
                                                   "status": status,
                                                   "blockBumber": blockNumber,
                                                   "timestamp": timestamp,
                                                   "Amount": Amount,
                                                   "from": From,
                                                   "to": to,
                                                   "Fees": Fees}}
            transaction_detail = {"result": 1, "data": {"transactions_data": transactions}}
        else:
            transaction_detail = {"result": 0, "errno": 102, "data": {}}
    else:
        transaction_detail = {"result": 0, "errno": 102, "data": {}}
    return HttpResponse(json.dumps(transaction_detail))
