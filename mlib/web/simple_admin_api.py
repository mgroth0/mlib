from wolframclient.language import wlexpr, wl

from mlib.boot.mlog import err, warn
from mlib.file import Folder
from mlib.term import log_invokation
from mlib.web.api import API
from mlib.web.html import arg_tags
from mlib.wolf.wolf_lang import CloudObject, StringSplit, If
from mlib.wolf.wolfpy import WolframService, wlapply, mwl, weval

class SimpleAdminAPI(API):
    @staticmethod
    def apifile_for(database_file):
        return Folder(database_file.parent)[f'{database_file.name_pre_ext}.wl']

    def __init__(self, database, *args, allow_get=True, allow_set=True, password=None, **kwargs):
        apiFile = self.apifile_for(database.file)

        self.database = database

        self.allow_get = allow_get
        self.allow_set = allow_set

        self.password = password

        super().__init__(apiFile, *args, **kwargs)

        if not self.offline_mode:
            weval(If(
                wl.Not(wl.FileExistsQ(wl.CloudObject("APIPasswords", wlexpr("$CloudSymbolBase")))),
                wlexpr('CloudSymbol["APIPasswords"]=<||>')
            ))
            weval(wlexpr(
                f'pwds = CloudSymbol["APIPasswords"]; pwds["{apiFile.abspath}"] = "{self.password}"; CloudSymbol["APIPasswords"] = pwds;'))
        else:
            warn(f'not pushing password for {self} because offline mode is switched one')
        apiFile.parent[f"{apiFile.name_pre_ext}_api_doc.text"].write(
            f"HTTP GET: {apiFile.wcurl}?<url encoded json obj>"
        )

    @log_invokation()
    def build_api_fun(self, serv: WolframService):
        serv.namespace = serv.fullMessage[self.KEY_ARG_NAME]
        serv.valueOrGetArgName = serv.fullMessage[self.VALUE_OR_GET_ARG_NAME]

        serv.co = CloudObject(self.database.file.abspath)
        serv.data = mwl.load_json(serv.co)
        serv.key = wlapply('Sequence', StringSplit(serv.namespace, "."))

        if self.password:
            @self.service.if_
            def _(blk: WolframService,
                  _condition=serv.xx["message"]['password'] == wl.Part(wl.CloudSymbol("APIPasswords"),
                                                                       self.apiFile.abspath)):
                blk._.exprs += [wlexpr('CloudSymbol["APILog"] = "simple_admin_api: ABORT"')]
                blk.abort()

        @self.service.if_
        def _(
                blk,
                _condition=wl.And(
                    serv.key == self.ALL_KEY,
                    wl.Not(serv.valueOrGetArgName == self.GET_CODE)
                )
        ):
            blk.abort()

        @self.service.if_
        def _(blk, _condition=serv.valueOrGetArgName == self.GET_CODE):
            if self.allow_get: return wl.If(
                blk.key == self.ALL_KEY,
                mwl.to_json(blk.data),
                mwl.to_json(blk.data[blk.key])
            )
            else: return "GET: NO ACCESS"
        @self.service.else_
        def _(blk):
            if self.allow_set:
                blk.data[blk.key] = blk.valueOrGetArgName
                blk.save_json(blk.co, blk.data)
            else:
                return "SET: NO ACCESS"



    def apiElements(self): return super().apiElements().extended(
        *arg_tags(
            API_GET_CODE=self.GET_CODE,
            API_KEY_ARG_NAME=self.KEY_ARG_NAME,
            ALL_KEY=self.ALL_KEY,
            API_VALUE_OR_GET_ARG_NAME=self.VALUE_OR_GET_ARG_NAME
        ).objs)



    @classmethod
    def cs(cls):
        super().cs()
        return '''
        class SimpleAdminAPI
          constructor: @api_url ->
          apiFun: (namespace,value,password=null) -> wcGET QueryURL(
                  @api_url, #inner.API_URL
                  {
                    message: JSON.stringify {
                      "#{inner.API_KEY_ARG_NAME}": namespace,
                      "#{inner.API_VALUE_OR_GET_ARG_NAME}": value,
                      'password': password
                    }
                  }
                )
          apiGET: (ns,password=null) -> apiFun(ns,inner.API_GET_CODE,password)
    '''

    GET_CODE = "GETTHISVARIABLEABCDEFG"
    KEY_ARG_NAME = "namespace"
    ALL_KEY = "ALL"
    VALUE_OR_GET_ARG_NAME = "setValue"
