DOFUSINVOKER = $(LOCALAPPDATA)/Ankama/Dofus/DofusInvoker.swf
FFDEC = $(CURDIR)/FFDec/ffdec.bat
DOFUS_SRC = $(CURDIR)/protocolBuilder/sources
SELECTCLASS = com.ankamagames.dofus.BuildInfos,com.ankamagames.dofus.network.++,com.ankamagames.jerakine.network.++
KEYS_DIR = $(CURDIR)/binaryData


.ONESHELL:
.PHONY: setup
setup:
	python -m venv .venv
	source .venv/Scripts/activate
	echo "$(CURDIR)" >> .venv/pyd2bot.pth
	pip install -r requirements.txt

update: decompile gen-protocol gen-msgClasses gen-msgShuffle extract-keys unpack-maps

decompile:
	@$(FFDEC) -config parallelSpeedUp=true -selectclass $(SELECTCLASS) -export script $(DOFUS_SRC) $(DOFUSINVOKER)

.ONESHELL:

extract-keys:
	@echo "Extracting keys..."
	@$(FFDEC) -config parallelSpeedUp=true -export binaryData $(KEYS_DIR) $(DOFUSINVOKER)
	@echo "Done."

gen-protocol:
	@echo "Generating protocol..."
	@python protocolBuilder/protocolParser.py $(DOFUS_SRC)
	@echo "Protocol generated"

gen-msgClasses:
	@echo "Generating msgClasses..."
	@python protocolBuilder/exportClasses.py
	@echo "msgClasses generated"

gen-msgShuffle:
	@echo "Generating msgShuffle..."
	@python protocolBuilder/extractMsgShuffle.py $(DOFUS_SRC)/scripts/com/ankamagames/dofus/network/MessageReceiver.as
	@echo "msgShuffle generated"

unpack-maps:
	@echo "Unpacking maps..."
	@python scripts/unpack_maps.py $(DOFUS_SRC)
	@echo "Maps unpacked"

deps:
	@pip install -r requirements.txt

startSniffer:
	@python -m snifferApp 

activate:
	. .venv/Scripts/activate

createAccount:
	@python $(CURDIR)/hackedLauncher/CredsManager.py $(entryName) $(login) $(password)

createBot:
	@python $(CURDIR)/pyd2bot/BotsDataManager.py $(botName) $(account) $(serverId) $(charachterId)

genKeys:
	@ssh-keygen -t rsa -b 2056 -m PEM -f $(PASS_ENC_KEYS)/id_rsa

test:
	@python $(CURDIR)/pyd2bot/main.py $(bot)

