=

class SnifferBuffer:
    def __init__(self) -> None:
        self.memory = []
        self.data = BinaryArray()
        self.expectedseq = 0

    def updateFromMemory(self):
        poped = []
        for seq, data in self.memory:
            if seq == self.expectedseq:
                poped.append(seq)
                self.data.append(data)
                self.expectedseq += seq + len(data)
        self.memory = [
            self.memory[i]
            for i in range(len(self.memory))
            if self.memory[i][0] not in poped
        ]

    def gather(self, currseq, currdata):
        print("curr : ", self.data, self.memory, self.expectedseq)
        self.updateFromMemory()
        if currseq == self.expectedseq:
            self.data.append(currdata)
            self.expectedseq = currseq + len(currdata)
        else:
            self.memory.append((currseq, currdata))
        self.updateFromMemory()
        print("end : ", self.data, self.memory, self.expectedseq)
        print("------------------------------------------------------")

    def getData(self):
        return "".join(self.data)


testcollector = SnifferBuffer()
#      0|1|2|3|4|5|6|7
# tgt "h|e|l|l|o|w| |w|o|r|l|d"

ch2 = 8, "orld"
ch0 = 0, "hel"
ch1 = 3, "low w"


testcollector.gather(*ch2)
testcollector.gather(*ch0)
testcollector.gather(*ch1)

print(testcollector.getData())
