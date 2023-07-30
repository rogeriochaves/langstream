"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[6653],{3905:(e,t,n)=>{n.d(t,{Zo:()=>p,kt:()=>d});var a=n(7294);function i(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function r(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);t&&(a=a.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,a)}return n}function s(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?r(Object(n),!0).forEach((function(t){i(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):r(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function o(e,t){if(null==e)return{};var n,a,i=function(e,t){if(null==e)return{};var n,a,i={},r=Object.keys(e);for(a=0;a<r.length;a++)n=r[a],t.indexOf(n)>=0||(i[n]=e[n]);return i}(e,t);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);for(a=0;a<r.length;a++)n=r[a],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(i[n]=e[n])}return i}var l=a.createContext({}),c=function(e){var t=a.useContext(l),n=t;return e&&(n="function"==typeof e?e(t):s(s({},t),e)),n},p=function(e){var t=c(e.components);return a.createElement(l.Provider,{value:t},e.children)},m="mdxType",u={inlineCode:"code",wrapper:function(e){var t=e.children;return a.createElement(a.Fragment,{},t)}},h=a.forwardRef((function(e,t){var n=e.components,i=e.mdxType,r=e.originalType,l=e.parentName,p=o(e,["components","mdxType","originalType","parentName"]),m=c(n),h=i,d=m["".concat(l,".").concat(h)]||m[h]||u[h]||r;return n?a.createElement(d,s(s({ref:t},p),{},{components:n})):a.createElement(d,s({ref:t},p))}));function d(e,t){var n=arguments,i=t&&t.mdxType;if("string"==typeof e||i){var r=n.length,s=new Array(r);s[0]=h;var o={};for(var l in t)hasOwnProperty.call(t,l)&&(o[l]=t[l]);o.originalType=e,o[m]="string"==typeof e?e:i,s[1]=o;for(var c=2;c<r;c++)s[c]=n[c];return a.createElement.apply(null,s)}return a.createElement.apply(null,n)}h.displayName="MDXCreateElement"},8280:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>l,contentTitle:()=>s,default:()=>u,frontMatter:()=>r,metadata:()=>o,toc:()=>c});var a=n(7462),i=(n(7294),n(3905));const r={sidebar_position:1},s="Chainlit Integration",o={unversionedId:"ui/chainlit",id:"ui/chainlit",title:"Chainlit Integration",description:"Chainlit is a UI that gives you a ChatGPT like interface for your chains, it is very easy to set up, it has a slick UI, and it allows you to visualize the intermediary steps, so it's great for development!",source:"@site/docs/ui/chainlit.md",sourceDirName:"ui",slug:"/ui/chainlit",permalink:"/litechain/docs/ui/chainlit",draft:!1,editUrl:"https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/docs/ui/chainlit.md",tags:[],version:"current",sidebarPosition:1,frontMatter:{sidebar_position:1},sidebar:"tutorialSidebar",previous:{title:"UI",permalink:"/litechain/docs/category/ui"},next:{title:"Code Examples",permalink:"/litechain/docs/examples/"}},l={},c=[],p={toc:c},m="wrapper";function u(e){let{components:t,...n}=e;return(0,i.kt)(m,(0,a.Z)({},p,n,{components:t,mdxType:"MDXLayout"}),(0,i.kt)("h1",{id:"chainlit-integration"},"Chainlit Integration"),(0,i.kt)("p",null,(0,i.kt)("a",{parentName:"p",href:"https://github.com/Chainlit/chainlit"},"Chainlit")," is a UI that gives you a ChatGPT like interface for your chains, it is very easy to set up, it has a slick UI, and it allows you to visualize the intermediary steps, so it's great for development!"),(0,i.kt)("p",null,"You can install it with:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre"},"pip install chainlit\n")),(0,i.kt)("p",null,"Then since we have access to all intermediary steps in LiteChain, integrating it with Chainlit is as easy as this:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},"from typing import Dict\nimport chainlit as cl\n\n@cl.on_message\nasync def on_message(message: str):\n    messages_map: Dict[str, cl.Message] = {}\n\n    async for output in chain(message):\n        if output.chain in messages_map:\n            cl_message = messages_map[output.chain]\n            await cl_message.stream_token(output.data.content)\n        else:\n            messages_map[output.chain] = cl.Message(\n                author=output.chain,\n                content=output.data.content,\n                indent=0 if output.final else 1,\n            )\n            await messages_map[output.chain].send()\n")),(0,i.kt)("p",null,"Here we are calling our chain, which is an ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/contrib/index.html#litechain.contrib.OpenAIChatChain"},(0,i.kt)("inlineCode",{parentName:"a"},"OpenAIChatChain")),", creating a new message as soon as a chain outputs, and streaming it new content as it arrives. We also ",(0,i.kt)("inlineCode",{parentName:"p"},"indent")," the message to mark it as an intermediary step if the output is not ",(0,i.kt)("inlineCode",{parentName:"p"},"final"),"."),(0,i.kt)("p",null,"Using our emoji translator example from before, this is how it is going to look like:"),(0,i.kt)("video",{src:"/litechain/img/chainlit-demo.mp4",width:"100%",controls:!0,style:{padding:"8px 0 32px 0"}}),(0,i.kt)("p",null,"Here is the complete code for an integration example:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python",metastring:'title="main.py"',title:'"main.py"'},'from typing import Dict, Iterable, List, Tuple, TypedDict\n\nimport chainlit as cl\n\nfrom litechain import debug\nfrom litechain.contrib import OpenAIChatChain, OpenAIChatDelta, OpenAIChatMessage\n\n\nclass Memory(TypedDict):\n    history: List[OpenAIChatMessage]\n\n\nmemory = Memory(history=[])\n\n\ndef save_message_to_memory(message: OpenAIChatMessage) -> OpenAIChatMessage:\n    memory["history"].append(message)\n    return message\n\n\ndef update_delta_on_memory(delta: OpenAIChatDelta) -> OpenAIChatDelta:\n    if memory["history"][-1].role != delta.role and delta.role is not None:\n        memory["history"].append(\n            OpenAIChatMessage(role=delta.role, content=delta.content)\n        )\n    else:\n        memory["history"][-1].content += delta.content\n    return delta\n\n\ntranslator_chain = OpenAIChatChain[Iterable[OpenAIChatDelta], OpenAIChatDelta](\n    "TranslatorChain",\n    lambda emoji_tokens: [\n        OpenAIChatMessage(\n            role="user",\n            content=f"Translate this emoji message {[token.content for token in emoji_tokens]} to plain english",\n        )\n    ],\n    model="gpt-4",\n)\n\nchain = (\n    debug(\n        OpenAIChatChain[str, OpenAIChatDelta](\n            "EmojiChatChain",\n            lambda user_message: [\n                *memory["history"],\n                save_message_to_memory(\n                    OpenAIChatMessage(\n                        role="user", content=f"{user_message}. Reply in emojis"\n                    )\n                ),\n            ],\n            model="gpt-3.5-turbo-0613",\n            temperature=0,\n        )\n    )\n    .map(update_delta_on_memory)\n    .and_then(debug(translator_chain))\n)\n\n@cl.on_message\nasync def on_message(message: str):\n    messages_map: Dict[str, Tuple[bool, cl.Message]] = {}\n\n    async for output in chain(message):\n        if "@" in output.chain and not output.final:\n            continue\n        if output.chain in messages_map:\n            sent, cl_message = messages_map[output.chain]\n            if not sent:\n                await cl_message.send()\n                messages_map[output.chain] = (True, cl_message)\n            await cl_message.stream_token(output.data.content)\n        else:\n            messages_map[output.chain] = (\n                False,\n                cl.Message(\n                    author=output.chain,\n                    content=output.data.content,\n                    indent=0 if output.final else 1,\n                ),\n            )\n')),(0,i.kt)("p",null,"You can run it with:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre"},"chainlit run main.py -w\n")))}u.isMDXComponent=!0}}]);