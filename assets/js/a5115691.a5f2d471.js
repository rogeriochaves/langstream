"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[9867],{3905:(e,n,t)=>{t.d(n,{Zo:()=>p,kt:()=>d});var a=t(7294);function i(e,n,t){return n in e?Object.defineProperty(e,n,{value:t,enumerable:!0,configurable:!0,writable:!0}):e[n]=t,e}function o(e,n){var t=Object.keys(e);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);n&&(a=a.filter((function(n){return Object.getOwnPropertyDescriptor(e,n).enumerable}))),t.push.apply(t,a)}return t}function r(e){for(var n=1;n<arguments.length;n++){var t=null!=arguments[n]?arguments[n]:{};n%2?o(Object(t),!0).forEach((function(n){i(e,n,t[n])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(t)):o(Object(t)).forEach((function(n){Object.defineProperty(e,n,Object.getOwnPropertyDescriptor(t,n))}))}return e}function l(e,n){if(null==e)return{};var t,a,i=function(e,n){if(null==e)return{};var t,a,i={},o=Object.keys(e);for(a=0;a<o.length;a++)t=o[a],n.indexOf(t)>=0||(i[t]=e[t]);return i}(e,n);if(Object.getOwnPropertySymbols){var o=Object.getOwnPropertySymbols(e);for(a=0;a<o.length;a++)t=o[a],n.indexOf(t)>=0||Object.prototype.propertyIsEnumerable.call(e,t)&&(i[t]=e[t])}return i}var s=a.createContext({}),c=function(e){var n=a.useContext(s),t=n;return e&&(t="function"==typeof e?e(n):r(r({},n),e)),t},p=function(e){var n=c(e.components);return a.createElement(s.Provider,{value:n},e.children)},h="mdxType",m={inlineCode:"code",wrapper:function(e){var n=e.children;return a.createElement(a.Fragment,{},n)}},u=a.forwardRef((function(e,n){var t=e.components,i=e.mdxType,o=e.originalType,s=e.parentName,p=l(e,["components","mdxType","originalType","parentName"]),h=c(t),u=i,d=h["".concat(s,".").concat(u)]||h[u]||m[u]||o;return t?a.createElement(d,r(r({ref:n},p),{},{components:t})):a.createElement(d,r({ref:n},p))}));function d(e,n){var t=arguments,i=n&&n.mdxType;if("string"==typeof e||i){var o=t.length,r=new Array(o);r[0]=u;var l={};for(var s in n)hasOwnProperty.call(n,s)&&(l[s]=n[s]);l.originalType=e,l[h]="string"==typeof e?e:i,r[1]=l;for(var c=2;c<o;c++)r[c]=t[c];return a.createElement.apply(null,r)}return a.createElement.apply(null,t)}u.displayName="MDXCreateElement"},1450:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>s,contentTitle:()=>r,default:()=>m,frontMatter:()=>o,metadata:()=>l,toc:()=>c});var a=t(7462),i=(t(7294),t(3905));const o={sidebar_position:4},r="Composing Chains",l={unversionedId:"chain-basics/composing_chains",id:"chain-basics/composing_chains",title:"Composing Chains",description:"If you are familiar with Functional Programming, the Chain follows the Monad Laws, this ensures they are composable to build complex application following the Category Theory definitions. Our goal on building LiteChain was always to make it truly composable, and this is the best abstraction we know for the job, so we adopted it.",source:"@site/docs/chain-basics/composing_chains.md",sourceDirName:"chain-basics",slug:"/chain-basics/composing_chains",permalink:"/litechain/docs/chain-basics/composing_chains",draft:!1,editUrl:"https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/docs/chain-basics/composing_chains.md",tags:[],version:"current",sidebarPosition:4,frontMatter:{sidebar_position:4},sidebar:"tutorialSidebar",previous:{title:"Working with Streams",permalink:"/litechain/docs/chain-basics/working_with_streams"},next:{title:"Type Signatures",permalink:"/litechain/docs/chain-basics/type_signatures"}},s={},c=[{value:"<code>map()</code>",id:"map",level:2},{value:"<code>and_then()</code>",id:"and_then",level:2},{value:"<code>collect()</code>",id:"collect",level:2},{value:"<code>join()</code>",id:"join",level:2},{value:"Standard nomenclature",id:"standard-nomenclature",level:2}],p={toc:c},h="wrapper";function m(e){let{components:n,...t}=e;return(0,i.kt)(h,(0,a.Z)({},p,t,{components:n,mdxType:"MDXLayout"}),(0,i.kt)("h1",{id:"composing-chains"},"Composing Chains"),(0,i.kt)("p",null,"If you are familiar with Functional Programming, the Chain follows the ",(0,i.kt)("a",{parentName:"p",href:"https://wiki.haskell.org/Monad_laws"},"Monad Laws"),", this ensures they are composable to build complex application following the Category Theory definitions. Our goal on building LiteChain was always to make it truly composable, and this is the best abstraction we know for the job, so we adopted it."),(0,i.kt)("p",null,"But you don't need to understand any Functional Programming or fancy terms, just to understand the five basic composition functions below:"),(0,i.kt)("h2",{id:"map"},(0,i.kt)("inlineCode",{parentName:"h2"},"map()")),(0,i.kt)("p",null,"This is the simplest one, the ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/index.html#litechain.Chain.map"},(0,i.kt)("inlineCode",{parentName:"a"},"map()"))," function transforms the output of a Chain, one token at a time as they arrive. The ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/index.html#litechain.Chain.map"},(0,i.kt)("inlineCode",{parentName:"a"},"map()"))," function is non-blocking, since it's processing the outputs as they come, so you shouldn't do heavy processing on it, although you can return asynchronous operations from it to await later."),(0,i.kt)("p",null,"Here is an example:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},'from litechain import Chain, as_async_generator, join_final_output\nimport asyncio\n\nasync def example():\n    # produces one word at a time\n    words_chain = Chain[str, str](\n        "WordsChain", lambda sentence: as_async_generator(*sentence.split(" "))\n    )\n\n    # uppercases each word and take the first letter\n    # highlight-next-line\n    accronym_chain = words_chain.map(lambda word: word.upper()[0])\n\n    return await join_final_output(accronym_chain("as soon as possible"))\n\nasyncio.run(example())\n#=> \'ASAP\'\n')),(0,i.kt)("p",null,'As you can see, the words "as", "soon", "as" and "possible" are generated one at a time, then the ',(0,i.kt)("inlineCode",{parentName:"p"},"map()")," function makes them uppercase and take the first letter, we join the final output later, resulting in ASAP."),(0,i.kt)("p",null,"Here we are using a basic ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/index.html#chain"},(0,i.kt)("inlineCode",{parentName:"a"},"Chain")),", but try to replace it with an ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/contrib/index.html#litechain.contrib.OpenAICompletionChain"},(0,i.kt)("inlineCode",{parentName:"a"},"OpenAICompletionChain"))," for example and you will see that the ",(0,i.kt)("inlineCode",{parentName:"p"},"map()")," function and all other composition functions work just the same."),(0,i.kt)("h2",{id:"and_then"},(0,i.kt)("inlineCode",{parentName:"h2"},"and_then()")),(0,i.kt)("p",null,"The ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/index.html#litechain.Chain.and_then"},(0,i.kt)("inlineCode",{parentName:"a"},"and_then()"))," is the true composition function, it's what\nallows you to compose two chains together, taking the output of one chain, and using as input for another one. Since generally we want the first chain to be finished to send the input to the next one, for example for building a prompt, the ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/index.html#litechain.Chain.and_then"},(0,i.kt)("inlineCode",{parentName:"a"},"and_then()"))," function is blocking, which means it will wait for all tokens\nto arrive from Chain A, collect them to a list, and only then call the Chain B."),(0,i.kt)("p",null,"For example:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},'from litechain import Chain, as_async_generator, join_final_output\nfrom typing import Iterable\nimport asyncio\n\nasync def example():\n    words_chain = Chain[str, str](\n        "WordsChain", lambda sentence: as_async_generator(*sentence.split(" "))\n    )\n\n    last_word_chain = Chain[Iterable[str], str]("LastWordChain", lambda words: list(words)[-1])\n\n    # highlight-next-line\n    chain = words_chain.and_then(last_word_chain)\n\n    return await join_final_output(chain("This is time well spent. DUNE!"))\n\nasyncio.run(example())\n#=> \'DUNE!\'\n')),(0,i.kt)("p",null,"In this example, ",(0,i.kt)("inlineCode",{parentName:"p"},"last_word_chain")," is a chain that takes only the last word that was generated, it takes an ",(0,i.kt)("inlineCode",{parentName:"p"},"Iterable[str]")," as input and produces ",(0,i.kt)("inlineCode",{parentName:"p"},"str")," (the last word) as output. There is no way for it to predict the last word, so of course it has to wait for the previous chain to finish, and ",(0,i.kt)("inlineCode",{parentName:"p"},"and_then()")," does that."),(0,i.kt)("p",null,"Also, not always the argument to ",(0,i.kt)("inlineCode",{parentName:"p"},"and_then()")," must be another chain, in this case it's simple enough that it can just be a lambda:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},"composed_chain = words_chain.and_then(lambda words: list(words)[-1])\n")),(0,i.kt)("p",null,"Then again, it could also be an LLM producing tokens in place of those chains, try it out with an ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/contrib/index.html#litechain.contrib.OpenAICompletionChain"},(0,i.kt)("inlineCode",{parentName:"a"},"OpenAICompletionChain")),"."),(0,i.kt)("h2",{id:"collect"},(0,i.kt)("inlineCode",{parentName:"h2"},"collect()")),(0,i.kt)("p",null,"The ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/index.html#litechain.Chain.collect"},(0,i.kt)("inlineCode",{parentName:"a"},"collect()"))," function blocks a Chain until all the values have been generated, and collects it into a list, kinda like what ",(0,i.kt)("inlineCode",{parentName:"p"},"and_then()")," does under the hood, but it doesn't take another chain as an argument, it takes no arguments, it just blocks the current chain transforming it into from a stream of items, to a single list item."),(0,i.kt)("p",null,"You can use ",(0,i.kt)("inlineCode",{parentName:"p"},"collect()")," + ",(0,i.kt)("inlineCode",{parentName:"p"},"map()")," to achieve the same as the ",(0,i.kt)("inlineCode",{parentName:"p"},"and_then()")," example above:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},'from litechain import Chain, as_async_generator, join_final_output\nimport asyncio\n\nasync def example():\n    words_chain = Chain[str, str](\n        "WordsChain", lambda sentence: as_async_generator(*sentence.split(" "))\n    )\n\n    # highlight-next-line\n    chain = words_chain.collect().map(lambda words: list(words)[-1])\n\n    return await join_final_output(chain("This is time well spent. DUNE!"))\n\nasyncio.run(example())\n#=> \'DUNE!\'\n')),(0,i.kt)("h2",{id:"join"},(0,i.kt)("inlineCode",{parentName:"h2"},"join()")),(0,i.kt)("p",null,"As you may have noticed, both ",(0,i.kt)("inlineCode",{parentName:"p"},"and_then()")," and ",(0,i.kt)("inlineCode",{parentName:"p"},"collect()")," produces a list of items from the previous chain output, this is because chains may produce any type of values, and a list is universal. However, for LLMs, the most common common case is for them to produce ",(0,i.kt)("inlineCode",{parentName:"p"},"str"),", which we want to join together as a final ",(0,i.kt)("inlineCode",{parentName:"p"},"str"),", for that, you can use the ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/index.html#litechain.Chain.join"},(0,i.kt)("inlineCode",{parentName:"a"},"join()"))," function."),(0,i.kt)("p",null,"The ",(0,i.kt)("inlineCode",{parentName:"p"},"join()")," function is also blocking, and it will only work if you chain is producing ",(0,i.kt)("inlineCode",{parentName:"p"},"str")," as output, otherwise it will show you a typing error."),(0,i.kt)("p",null,"Here is an example:"),(0,i.kt)("pre",null,(0,i.kt)("code",{parentName:"pre",className:"language-python"},'from litechain import Chain, as_async_generator, join_final_output\nimport asyncio\n\nasync def example():\n    pairings_chain = Chain[None, str](\n        "PairingsChain", lambda _: as_async_generator("Human ", "and ", "dog")\n    )\n\n    # highlight-start\n    chain = pairings_chain.join().map(\n        lambda pairing: "BEST FRIENDS!" if pairing == "Human and dog" else "meh"\n    )\n    # highlight-end\n\n    return await join_final_output(chain(None))\n\nasyncio.run(example())\n#=> \'BEST FRIENDS!\'\n')),(0,i.kt)("p",null,"It is common practice to ",(0,i.kt)("inlineCode",{parentName:"p"},"join()")," an LLM output before injecting it as another LLM input."),(0,i.kt)("h2",{id:"standard-nomenclature"},"Standard nomenclature"),(0,i.kt)("p",null,"Now that you know the basic composing functions, it's also interesting to note everything in LiteChain also follow the same patterns, for example, for the final output we have the utilities ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/index.html#litechain.filter_final_output"},(0,i.kt)("inlineCode",{parentName:"a"},"filter_final_output()")),", ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/index.html#litechain.collect_final_output"},(0,i.kt)("inlineCode",{parentName:"a"},"collect_final_output()"))," and ",(0,i.kt)("a",{parentName:"p",href:"pathname:///reference/litechain/index.html#litechain.join_final_output"},(0,i.kt)("inlineCode",{parentName:"a"},"join_final_output()")),", you can see they are using the same ",(0,i.kt)("inlineCode",{parentName:"p"},"filter"),", ",(0,i.kt)("inlineCode",{parentName:"p"},"collect")," and ",(0,i.kt)("inlineCode",{parentName:"p"},"join")," names, and they work as you would expect them to."),(0,i.kt)("p",null,"Now, that you know how to transform and compose chains, keep on reading to understand why type signatures are important to LangChain."))}m.isMDXComponent=!0}}]);