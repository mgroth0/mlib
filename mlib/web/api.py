from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Union, ClassVar

from wolframclient.language import wlexpr, wl

from mlib.boot import log
from mlib.boot.mlog import warn
from mlib.file import File
from mlib.web.web import arg_tags
from mlib.wolf.wolf_lang import APIFunction, Function, If
from mlib.wolf.wolfpy import WolframService, inputForm, APIRule, wlexprc, wlblock, FormatWLInput, PERMISSIONS, MWL, mwl

@dataclass
class API(ABC):
    offline_mode: ClassVar[bool] = False
    apiFile: Union[str, File]
    def __post_init__(self):
        self.service = WolframService()
        self.build_api_fun(self.service)
        expression = APIFunction(
            [
                APIRule(
                    "message",
                    "String"
                ),
                APIRule("index", "Integer"),
                APIRule("total", "Integer"),
                APIRule("messageID", "String"),
            ],
            Function(
                wlexprc('xx'),
                wlblock(
                    wlexpr('CloudSymbol["APILog"] = "started api base"'),
                    If(
                        wl.Not(wl.FileExistsQ(wl.CloudObject("APIMessages", wlexpr("$CloudSymbolBase")))),
                        wlexpr('CloudSymbol["APIMessages"]=<||>')
                    ),
                    wl.For(
                        wlexpr('i=1'),
                        wlexpr('i<=Length@Keys[CloudSymbol["APIMessages"]]'),
                        wlexpr('i++'),
                        If(
                            wlexpr(
                                '((UnixTime[] * 1000) - ToExpression[StringSplit[(Keys[CloudSymbol["APIMessages"]])[[i]],"***"][[2]]]) > 60000'),
                            wlexpr(
                                'apiMessages = CloudSymbol["APIMessages"]; apiMessages = KeyDrop[apiMessages,Keys[CloudSymbol["APIMessages"]][[i]]]; CloudSymbol["APIMessages"] = apiMessages;')
                        )
                    ),
                    If(
                        wl.Not(wl.KeyExistsQ(wl.CloudSymbol("APIMessages"), wlexpr('xx["messageID"]'))),
                        wlexpr(
                            'APIMessages=CloudSymbol["APIMessages"]; APIMessages[xx["messageID"]] = {}; CloudSymbol["APIMessages"] = APIMessages;')
                    ),
                    wlexpr(
                        'thisMessageData = <|"i"->xx["index"],"t"->xx["total"],"m"->xx["message"]|>; APIMessages=CloudSymbol["APIMessages"]; myMessages = APIMessages[xx["messageID"]]; myMessages = Append[myMessages,thisMessageData]; APIMessages[xx["messageID"]] = myMessages; CloudSymbol["APIMessages"] = APIMessages;'
                    ),
                    If(
                        wlexpr(
                            'thisMessageData["i"]==thisMessageData["t"]'
                        ),
                        wlblock(
                            wlexpr(
                                'fullMessage = StringJoin[Map[Function[xxxx,xxxx["m"]],CloudSymbol["APIMessages"][xx["messageID"]]]]'
                            ),
                            wlexpr('fullMessage = ImportString[fullMessage,"RawJSON"]'),
                            *self.service.build_expressions(),
                        )
                    ),
                )
            )
        )
        expression = FormatWLInput(inputForm(expression))

        self.apiFile = File(self.apiFile)
        assert self.apiFile.ext == 'wl', f'extension of {self.apiFile} is {self.apiFile.ext}'
        self.apiURL = self.apiFile.wcurl
        self.apiFile.write(expression)
        if not self.offline_mode:
            MWL.cloud_deploy(expression, self.apiFile, PERMISSIONS.PUBLIC)
        else:
            warn(f'not deploying {self} because offline mode is switched one')
        log(f'{self.apiURL=}')

    def apiElements(self): return arg_tags(API_URL=self.apiURL)

    _GOT_CS = set()
    @classmethod
    @abstractmethod
    def cs(cls):
        assert cls not in API._GOT_CS
        API._GOT_CS.add(cls)

    @abstractmethod
    def build_api_fun(self, serv: WolframService): pass
