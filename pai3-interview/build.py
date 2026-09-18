#!/usr/bin/env python3
"""Build EN + UA PAI3 interview cheatsheet HTML pages.

Generates two self-contained HTML files in Claude Code style:
dark theme, monospace, minimalist, hover tooltips on every technical term.

Source: /home/taras/projects/career/dou/pai3-network/ai-systems-engineer/questionnaire-answers.md
        (the canonical pre-interview answers grounded in real projects)

Output: /home/taras/projects/career/taras-polishchuk.github.io/pai3-interview/{index,ua}.html
        Live:  https://taras-polishchuk.github.io/pai3-interview/
"""

from pathlib import Path
import json
import html as ihtml

OUT_DIR = Path("/home/taras/projects/career/taras-polishchuk.github.io/pai3-interview")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# UA TRANSLATIONS — Ukrainian tooltip + modal body for every glossary term.
# Mirrors the keys of GLOSSARY. Each entry: {term, short, long}.
# Style: native Ukrainian, terse (per operator's standing rule), but precise
# enough that a 15-year-old or a non-technical friend can follow.
# ============================================================================

UA_GLOSSARY = {
    "pai3": {"term": "PAI3 Network", "short": "Децентралізована AI-мережа, де все працює локально — без хмари і без центрального контролю. Мета: приватний AI для регульованих середовищ.", "long": "PAI3 Network — це децентралізована AI-мережа для випадків, де приватність даних, локальний контроль і офлайн-робота важливіші за масштаб. Стек цілить у PowerNodes (edge-залізо) і відкидає залежність від хмари. Медичний софт / інтранет — типова ціль: дані пацієнтів ніколи не виходять з локальної мережі."},
    "powernode": {"term": "PowerNode", "short": "Edge-залізо, на якому локально живе AI-модель. Фізична машина всередині клієнтської мережі.", "long": "PowerNode — це edge-обчислювальний пристрій PAI3: фізична (або віртуальна) машина всередині інтранету клієнта, на якій живе локальна LLM, agent runtime і пов'язані сервіси. PowerNodes керуються як флот — оновлення, model rollouts і health checks пушаться на кожну ноду окремо. «Децентралізована» частина PAI3 означає, що немає центрального inference-кластера: кожен PowerNode сам запускає модель."},
    "intranet": {"term": "інтранет", "short": "Приватна мережа всередині однієї організації. Немає доступу з публічного інтернету. Модель ніколи не виходить за цю межу.", "long": "Інтранет — це закрита мережа, до якої мають доступ тільки свої користувачі і пристрої організації. Для медичного софту це критично: дані пацієнтів, промпти і виходи моделі ніколи не залишають мережу лікарні чи клініки. Протилежність SaaS — без мультитенантної хмари і спільної інфраструктури."},
    "ollama": {"term": "Ollama", "short": "Утиліта, що запускає LLM локально як простий HTTP-сервер. Тягне готові моделі, віддає OpenAI-сумісний API на localhost.", "long": "Ollama — це зручний рантайм для локальних LLM. Один раз `ollama pull mistral` — і маєш модель, що віддає completion-запити на `http://localhost:11434`. Сама вирішує завантаження моделі, дефолтну квантизацію (Q4_K_M), fallback CPU/GPU і віддає OpenAI-подібний API — тож код застосунку не треба переписувати при перемиканні між хмарою і локальним інференсом."},
    "gguf": {"term": "GGUF", "short": "Формат файлу для квантизованих LLM. Те, що Ollama / llama.cpp реально читає з диска.", "long": "GGUF — сучасний нащадок GGML. Це формат одного файлу, де разом лежать ваги моделі, токенайзер і метадані, і mmap-иться швидко. Рівні квантизації в одній родині: Q2_K (найменший, найслабший), Q4_K_M (стандартний sweet spot), Q6_K, Q8_0. Trade-off — пам'ять проти якості: менші файли влізають у слабше залізо, але модель трохи тупіша."},
    "quantization": {"term": "квантизація", "short": "Стиснення моделі через меншу розрядність ваг (16-біт → 4-біт). Економить у 3-4 рази пам'яті з невеликою втратою якості.", "long": "Квантизація знижує точність кожної ваги з 16- або 32-бітного float до 4-біт, 8-біт і т.д. Розмір на диску і сліди в RAM падають кардинально (4-біт ≈ у 4 рази менше), inference прискорюється, з невеликою втратою якості. Поширені формати: GGUF, GPTQ, AWQ, bitsandbytes (4-біт). Саме завдяки квантизації модель 7B-13B можна запустити на edge-залізі з 8-16 ГБ RAM."},
    "q4-k-m": {"term": "Q4_K_M", "short": "Конкретний рівень 4-бітної GGUF-квантизації. Стандартний sweet spot — маленький, швидкий, ~99% якості повної моделі.", "long": "Q4_K_M — один з k-quant варіантів у GGUF. «Q4» = 4-бітні ваги, «K» = k-quant метод (різні шари — різна точність), «M» = medium (між Q4_K_S меншим і Q4_K_L більшим). Це найпоширеніший дефолт в Ollama, бо втрата якості проти повної точності маленька для типових chat/RAG задач, а розмір ~4 ГБ для 7B моделі."},
    "lora": {"term": "LoRA", "short": "Low-Rank Adaptation. Маленька тренована «нашлєпка» поверх замороженої базової моделі. Дешево тренувати, дешево міняти.", "long": "LoRA дотреновує модель, вставляючи дві маленькі тренованих матриці в кожен трансформер-шар, поки оригінальні ваги заморожені. Результат — крихітний файл-адаптер (часто <100 МБ), що фіксує нову поведінку. Можна мати десятки LoRA під різні задачі і підвантажувати потрібну без копіювання всієї бази."},
    "qlora": {"term": "QLoRA", "short": "LoRA плюс 4-бітна квантизація базової моделі. Тренує адаптери на моделі, що влізає у пам'ять звичайної GPU.", "long": "QLoRA = квантизована база + LoRA-адаптер. База вантажиться в 4-біт (через bitsandbytes), тож влізає у 16-24 ГБ VRAM. Зверху тренуються маленькі LoRA-адаптери. Це те, що робить fine-tuning 7B-13B моделі реальним на одній споживчій GPU замість кластера з кількох A100."},
    "pytorch": {"term": "PyTorch", "short": "Домінуючий Python-фреймворк для тренування і запуску нейромереж. Стандарт для будь-якої кастомної модельної роботи.", "long": "PyTorch — де-факто фреймворк для deep learning-досліджень і прод-тренування. Майже кожна опенсорс-модель (LLaMA, Mistral, Stable Diffusion) поставляється з PyTorch-вагами і PyTorch-кодом тренування. Для LoRA/QLoRA fine-tuning канонічний стек — PyTorch + Hugging Face Transformers + PEFT + bitsandbytes."},
    "peft": {"term": "PEFT", "short": "Parameter-Efficient Fine-Tuning. Бібліотека Hugging Face, що реалізує LoRA / QLoRA / адаптери поверх будь-якої базової моделі.", "long": "PEFT (Hugging Face) — стандартна бібліотека parameter-efficient fine-tuning. Обгортає будь-яку базову модель і додає маленькі тренеровані адаптери (LoRA, IA3, prefix-tuning), не торкаючись заморожених ваг. У парі з `bitsandbytes` для 4-бітного завантаження — це канонічний рецепт fine-tuning 7B+ на одній GPU."},
    "bitsandbytes": {"term": "bitsandbytes", "short": "Python-бібліотека для 4-бітного / 8-бітного завантаження моделей у PyTorch. Разом з PEFT — основа QLoRA.", "long": "bitsandbytes (bnb) дає примітиви 4-бітної і 8-бітної квантизації для PyTorch. `BitsAndBytesConfig` дозволяє Hugging Face-моделі вантажитись у 4-біт NF4 з подвійною квантизацією — пам'ять падає у ~4 рази. Це фундамент, на якому стоїть QLoRA."},
    "transformer": {"term": "трансформер", "short": "Архітектура нейромережі, на якій побудовані сучасні LLM. Шари self-attention, 32-80+ шарів. «T» в GPT.", "long": "Архітектура трансформера (Vaswani et al., 2017) — основа майже всіх сучасних LLM. Використовує self-attention: кожен токен дивиться на кожен інший токен у вікні контексту, шари ставляться один на одного. Кожен шар має attention-голови і feed-forward блок. Fine-tuning зазвичай чіпає адаптерні ваги в attention-шарах, не feed-forward."},
    "langchain": {"term": "LangChain", "short": "Python / TypeScript фреймворк для ланцюгів LLM-викликів, тулів і пам'яті. Найпоширеніший фреймворк для LLM-застосунків.", "long": "LangChain дає абстракції для промптів, тулів, ретриверів, пам'яті і ланцюгів — будівельних блоків LLM-застосунку. У 2024-2025 для stateful agent-роботи він поступається LangGraph, але лишається стандартом для простіших RAG і tool-use пайплайнів."},
    "langgraph": {"term": "LangGraph", "short": "Stateful граф-фреймворк для агентів від команди LangChain. Агент = нода, переходи = ребра, стан — явний.", "long": "LangGraph моделює агентну систему як спрямований граф: ноди — функції (LLM-виклики, виклики тулів, human approval), ребра — переходи (умовні чи фіксовані), спільний типізований `State` тече через граф. Підтримує checkpointing (відновлення після краху), цикли, переривання для human-in-the-loop. Наступник LangChain для серйозної multi-agent роботи."},
    "rag": {"term": "RAG", "short": "Retrieval-Augmented Generation. Модель відповідає, використовуючи чанки тексту, які витягнуті з векторної БД під час запиту.", "long": "RAG — домінуючий патерн для «прив'язки» LLM до приватних або свіжих даних. На момент запиту питання користувача ембедиться у вектор, схожі чанки витягуються з векторної БД (pgvector, Pinecone, Weaviate) і кладуться в промпт як контекст. Модель відповідає, спираючись на ці чанки, а не лише на свої тренувальні дані. Менше галюцинацій, є за що процитувати."},
    "pgvector": {"term": "pgvector", "short": "Розширення Postgres, що додає векторний пошук у звичайну Postgres-таблицю. RAG без окремої векторної БД.", "long": "pgvector додає тип колонки `vector` і ANN-індекси (HNSW, IVFFlat) до PostgreSQL. Для команд, які вже використовують Postgres, це найпростіший шлях до RAG — ембеддинги лежать поруч з реляційними даними, один шар транзакцій, одна стратегія бекапу. Trade-off: на мільйонах векторів спеціалізовані векторні БД (Pinecone, Qdrant) масштабуються краще."},
    "vector-embedding": {"term": "ембеддинг", "short": "Список чисел (напр. 1536 float-ів), що представляє зміст тексту. Схожі тексти → схожі вектори.", "long": "Ембеддинг — вектор фіксованої довжини, який видає модель (напр. OpenAI `text-embedding-3-small` видає 1536 чисел). Семантично схожі тексти дають вектори, близькі за косинусною відстанню. Використовується для семантичного пошуку, RAG-витягування, кластеризації, класифікації."},
    "cosine-similarity": {"term": "косинусна схожість", "short": "Як виміряти, що два вектори ембеддингів означають одне й те саме. Від -1 (протилежне) до 1 (те саме).", "long": "Косинусна схожість = dot product двох векторів / добуток їх довжин. Ігнорує довжину вектора і дивиться лише на напрямок — це правильна метрика для ембеддингів (довжина не має значення, значення має напрямок). Для RAG top-k retrieval за косинусною схожістю вибирає чанки, що найбільш релевантні запиту."},
    "agent": {"term": "агент", "short": "LLM-керована програма, яка сама вирішує, що робити далі, за фіксованим сценарієм. Цикл: подумав → діяв → спостеріг.", "long": "LLM-агент — це система, де сама модель обирає дії (виклики тулів, пошук, виконання коду) у циклі до якоїсь зупинки. На відміну від ланцюга (фіксована послідовність) чи пайплайна (детерміністичний граф). Агенти потужні, але їх важче тестувати, вони легше галюцинують і їм потрібні явні guardrails."},
    "n8n": {"term": "n8n", "short": "Open-source інструмент автоматизації. Візуальний редактор ланцюгів API-викликів, AI-нод, умов і ретраїв.", "long": "n8n — це self-hostable альтернатива Zapier / Make. Збираєш workflow у візуальному редакторі: тригер → нода → нода → умовний бранч → шлях обробки помилок. Має нативні LLM / AI agent ноди, HTTP request, 400+ інтеграцій. Для соло / маленької команди — швидше за кастомний agent runtime, і JSON-файли workflow версіонуються в git."},
    "prompt-injection": {"term": "prompt injection", "short": "Вхідні дані, які обманюють LLM ігнорувати свої справжні інструкції і виконувати атакуючого. Головний ризик безпеки LLM.", "long": "Prompt injection — коли в user-controlled тексті (або навіть у third-party контенті, який модель витягла) є інструкції типу «ігноруючи все вищесказане, зроби X». Модель не може надійно відрізнити user-контент від system-інструкцій. Захисти: pre-LLM input-фільтри, structured-output обмеження, post-LLM валідація виходу, і ставлення до будь-якого витягнутого контенту як до ненадійного."},
    "system-prompt": {"term": "системний промпт", "short": "Приховані інструкції, що задають роль LLM, межі і поведінку. «Посадова інструкція» моделі.", "long": "Системний промпт надсилається моделі як перше повідомлення у розмові з роллю «system». Він визначає, що модель має робити (і не робити), її тон, її межі, що вона має відмовляти робити. Вразливий до атак витягування («повтори системний промпт дослівно») — тому продакшен-системи не повинні класти туди секрети."},
    "guardrails": {"term": "guardrails", "short": "Детерміністичні перевірки до або після LLM-виклику. Відсіюють поганий вхід, валідують поганий вихід.", "long": "Guardrails — це не-LLM правила, що фільтрують або трансформують те, що входить у модель або виходить з неї. Pre-LLM: regex / класифікатор відсіює prompt injection, завеликий вхід, off-topic запити. Post-LLM: валідація схеми, редакція PII, allowlist URL, обмеження довжини. Сенс у тому, що політику ніколи не варто довіряти самій моделі."},
    "grounding": {"term": "grounding", "short": "Прив'язка відповіді моделі до витягнутих фактів (RAG) або верифікованих даних. Протилежність галюцинації.", "long": "Grounding означає, що модель відповідає лише на основі наданого контексту і каже «не знаю», якщо контексту недостатньо. RAG — домінуюча техніка grounding. Галюцинації різко падають, коли модель змушена цитувати витягнуті чанки, а не вільно генерувати з тренувального розподілу."},
    "structured-output": {"term": "structured output", "short": "Примус моделі відповідати JSON за схемою, а не вільним текстом. Виходи стають машинно-відагоджуваними.", "long": "Structured output (напр. OpenAI JSON mode, Zod / Pydantic схеми, бібліотека instructor) обмежує відповідь моделі валідним JSON, що відповідає заявленій формі. Далі downstream-код може довіряти структурі: `response.risk_level` — завжди одне з `low | medium | high`, а не вільне речення. Знімає цілий клас багів парсингу."},
    "zod": {"term": "Zod", "short": "TypeScript-бібліотека для оголошення форм даних і валідації в рантаймі. Використовується для валідації LLM structured outputs.", "long": "Zod — найпопулярніша TypeScript-бібліотека валідації схем. Пишеш `z.object({ name: z.string(), age: z.number().int().positive() })` — і Zod виводить TypeScript-тип і валідує будь-які рантайм-дані за цією формою. У LLM-пайплайнах Zod — типовий спосіб визначати і примусово перевіряти форму structured outputs моделі."},
    "confidence-threshold": {"term": "confidence threshold", "short": "Мінімальний retrieval score, нижче якого асистент відмовляється відповідати замість здогадуватися.", "long": "Коли RAG витягує чанки контексту, кожен має свій score схожості. Confidence threshold — це відсічка: чанки вище порогу = «модель має достатньо контексту», нижче = «контекст заслабкий, refuse або ескалація». Тюнінг цього порога — це trade-off між хибними відмовами і галюцинованими відповідями."},
    "docker": {"term": "Docker", "short": "Пакує застосунок + залежності в один контейнер. Однакова поведінка на будь-якому Linux-хості.", "long": "Docker використовує OS-рівневу віртуалізацію, щоб запакувати застосунок з бібліотеками, конфігами і рантаймом у образ контейнера. Образ працює однаково на ноуті розробника, CI-сервері чи прод-ноді. Для AI-інференсу зазвичай контейнеризують model-сервер (Ollama, vLLM, TGI), щоб деплої були відтворюваними."},
    "kubernetes": {"term": "Kubernetes", "short": "Оркестратор контейнерів. Керує сотнями контейнерів на багатьох машинах. Важка інфраструктура.", "long": "Kubernetes (K8s) — індустріальний стандарт оркестрації контейнеризованих навантажень: scheduling, self-healing, rolling updates, service discovery. Потужний, але важкий — потребує control plane, мережевого шару, ingress controllers. PAI3 явно уникає: «Не покладатися на Kubernetes, Docker чи cloud pipelines»."},
    "cloudflare-tunnel": {"term": "Cloudflare Tunnel", "short": "Захищений outbound-тунель, що відкриває локальний сервіс в інтернет без відкриття портів у фаєрволі.", "long": "Cloudflare Tunnel (`cloudflared`) запускається процесом на твоїй машині і відкриває outbound-only з'єднання до Cloudflare edge. Ти отримуєш публічний HTTPS-URL, що проксує у твій локальний сервіс. Без правил inbound на фаєрволі, без потреби у публічній IP. Корисно для відкриття self-hosted n8n чи portfolio-демо без port-forwarding."},
    "tailscale": {"term": "Tailscale", "short": "Mesh-VPN, що з'єднує твої пристрої у приватну мережу через WireGuard. Zero-config, identity-based.", "long": "Tailscale будує WireGuard mesh-VPN між твоїми пристроями (ноут, сервер, телефон), використовуючи твою існуючу identity (Google, GitHub, Microsoft login). Без port forwarding, без правил фаєрволу. Кожен пристрій отримує стабільну IP у tailnet (100.x.y.z). Для ops — це найшвидший спосіб дістатися до homelab-сервера звідуки."},
    "coolify": {"term": "Coolify", "short": "Self-hosted PaaS. Деплоїть застосунки і бази даних з веб-інтерфейсу без Kubernetes. «Heroku на своєму сервері».", "long": "Coolify — open-source self-hostable платформа-як-сервіс. Керує Docker-контейнерами, базами даних, SSL через Let's Encrypt і reverse proxy через Traefik — все з веб-інтерфейсу. Для соло-розробників чи маленьких команд замінює Vercel / Fly.io / Heroku на homelab-альтернативу без Kubernetes."},
    "systemd": {"term": "systemd", "short": "Linux-менеджер сервісів. Запускає застосунок на буті, рестартить при краху, пише логи. «start.sh» продакшен-Linux.", "long": "systemd — стандартний init на сучасному Linux. Пишеш unit-файл `.service`, як запускати застосунок, потім `systemctl enable --now myapp` — він стартує на буті і авто-рестартить при збої. Для не-Docker локальних деплоїв (стиль PAI3) systemd — це еквівалент Docker restart policy."},
    "observability": {"term": "observability", "short": "Можливість зрозуміти, що робить твоя система, з її виходів — логів, метрик, трейсів. Потрібно для дебагу AI у продакшені.", "long": "Observability — дисципліна зробити внутрішній стан системи зрозумілим з зовнішніх виходів. Три стовпи: логи (дискретні події), метрики (агреговані числа за часом), трейси (шлях запиту через сервіси). Для AI-систем потрібні ще prompt/response логи, retrieval scores і розподіл confidence — LLM недетерміністичний, тож класичний дебаг не працює."},
    "metrics": {"term": "метрики", "short": "Числа, що підсумовують поведінку системи за часом. Request rate, error rate, p99 latency. Дашборди Grafana.", "long": "Метрики — скалярні time-series значення: запити/секунду, error rate, перцентилі латенсі, GPU utilisation, tokens/секунду. Зберігаються у Prometheus чи подібному. Для AI: використання токенів, розподіл retrieval confidence, model refusal rate."},
    "logging": {"term": "логи", "short": "Запис подій з таймстемпами у файл чи сервіс. «Що сталося» — запис твоєї системи.", "long": "Логи — append-only записи подій: `[2026-09-18 16:01:23] POST /api/inference 200 1.4s model=mistral-7b-q4`. Для AI-систем варто логувати промпт, відповідь, витягнуті чанки і confidence — але обережно з PII і секретами. Структуровані JSON-логи (одна подія на рядок) легше запитувати, ніж plain text."},
    "governance": {"term": "governance", "short": "Правила, ролі і процеси рев'ю, що вирішують, хто і що може робити з системою. Особливо важливо для AI, що впливає на людей.", "long": "Governance — це шар над кодом: хто може деплоїти, хто затверджує зміну моделі, які дані дозволені, який процес рев'ю інцидентів. Для медичного AI це стає регуляцією: HIPAA, MDR, audit trails, записи змін моделей, процедури rollback. «Governance» тут — це людино-політичний шар, не LLM."},
    "hipaa": {"term": "HIPAA", "short": "US-ський закон про приватність у медицині. Регулює, як треба поводитися з даними пацієнтів. Софт, що торкається patient data, має відповідати.", "long": "Health Insurance Portability and Accountability Act (1996). Встановлює правила для protected health information (PHI): хто може бачити, як зберігати, повідомлення про витоки, audit-логи. Будь-який софт, що обробляє дані пацієнтів — включно з LLM-асистентом, що читає клінічні нотатки — має бути спроєктований з урахуванням HIPAA."},
    "phi": {"term": "PHI", "short": "Protected Health Information. Будь-які дані, що ідентифікують пацієнта і стосуються його здоров'я. Поводитися обережно.", "long": "PHI — юридичний термін для будь-яких індивідуально ідентифіковних медичних даних: ім'я + діагноз, MRN, дата народження + візит, навіть IP у парі з медичною інформацією. Відправляти PHI у third-party API (включно з LLM API) без Business Associate Agreement — це порушення HIPAA. Це одна з причин, чому медичний AI працює локально."},
    "audit-trail": {"term": "audit trail", "short": "Незмінний запис того, хто що і коли зробив. Обов'язковий для регульованих індустрій (медицина, фінанси).", "long": "Audit trail — tamper-evident лог кожної дії в системі: хто доступився до яких даних, хто змінив який сетап, хто задеплоїв яку версію моделі. Для регульованого AI (медичного, фінансового) audit trail — не опція, а те, що ти показуєш регулятору, коли щось пішло не так."},
    "human-in-the-loop": {"term": "human-in-the-loop", "short": "Людина має затвердити або скоригувати вихід AI перед тим, як він спрацює. Патерн для високо-ризикових рішень.", "long": "Human-in-the-loop (HITL) — workflow, де AI пропонує дію чи відповідь, але людина рев'ює і затверджує, перш ніж станеться щось незворотне. Стандарт у медичному AI: модель готує чернетку, клініцист підписує. LangGraph підтримує це нативно через interrupt-ноди."},
    "rollback": {"term": "rollback", "short": "Повернення системи до попередньої відомо-робочої версії. Безпечна кнопка, коли нова модель чи деплой ламає.", "long": "Rollback — можливість швидко повернутися до попереднього робочого стану. Для AI-моделей: тримай старі checkpoint-и, версіонуй адаптери, май протестовану процедуру заміни. Для деплоїв: тримай попередній образ контейнера, використовуй blue/green чи canary релізи. Різниця між інцидентом і катастрофою — чи rollback займає 30 секунд чи 30 годин."},
    "checkpoint": {"term": "checkpoint", "short": "Збережений знімок моделі чи стану workflow. Відновлення тренування, після краху, чи для rollback.", "long": "Checkpoint — збережений знімок. Для тренування моделі: збережені ваги на кроці N (щоб можна було продовжити, якщо воно крахнуло). Для LangGraph workflow: поточний стан кожної ноди (щоб багатогодинний запуск агента можна було продовжити після рестарту сервера). Для інференсу: заморожена версія моделі, до якої можна відкотитися."},
    "blue-green": {"term": "blue/green", "short": "Деплой через паралельний запуск нової і старої версій, потім перемикання трафіку. Zero-downtime, миттєвий rollback.", "long": "Blue/green deployment: запускаєш поточну версію («blue») і нову («green») одночасно. Весь трафік іде на blue. Тестуєш green у продакшені. Коли green верифікований, перемикаєш load balancer на green. Якщо green ламається — перемикаєш назад на blue: миттєвий rollback, без паніки під тиском."},
    "load-balancer": {"term": "load balancer", "short": "Сервер, що розподіляє вхідні запити між кількома бекендами. Вхідні двері масштабованого сервісу.", "long": "Load balancer (NGINX, HAProxy, Cloudflare, AWS ALB) приймає вхідний трафік і пересилає кожен запит на один з N бекенд-інстансів. Розподіляє навантаження, дає failover (якщо один бекенд впав — слати на решту), дає zero-downtime деплої (blue/green). Для AI: роутити на PowerNode з найменшим поточним навантаженням."},
    "p99": {"term": "p99 латенсі", "short": "Найповільніші 1% запитів. Справжня цифра «user experience» — p50 бреше, p99 ні.", "long": "p99 латенсі — 99-й перцентиль: 99% запитів завершуються швидше за це, лише 1% — повільніші. p50 (медіана) ховає найгірші випадки. Для AI: p99 включає cold start першого запиту після простою, повільний токен на довгому контексті, timeout retry. Продакшен-SLO зазвичай пишуть за p99."},
    "throughput": {"term": "throughput", "short": "Скільки запитів (або токенів) за секунду витримує система. Потужність, не швидкість.", "long": "Throughput — швидкість завершеної роботи: запити/сек, токени/сек, інференси/годину. Для LLM-сервінгу: токени за секунду на GPU. Це не те саме, що латенсі — система може бути швидкою (низька латенсі), але low-throughput (малий batch size, не вистачає GPU-пам'яті), або високо-throughput, але повільною на запит. Для медичних асистентів throughput важливіший за пікову швидкість."},
    "tokens-per-second": {"term": "токени/сек", "short": "Як швидко модель генерує вихід. ~30 tok/s = читабельно, ~100 tok/s = миттєво. Видима користувачем метрика швидкості.", "long": "LLM генерують текст по одному токену (~4 символи в англійській). Tokens per second — видима користувачем швидкість моделі. На 7B з Q4-квантизацією на сучасній GPU: 50-100 tok/s. На CPU: 5-15 tok/s. Для chat UX хочеться мінімум 30 tok/s; нижче — відчуття затримки."},
    "edge-deployment": {"term": "edge deployment", "short": "Запуск моделі близько до даних (ноут, сервер лікарні, IoT-пристрій) замість центральної хмари.", "long": "Edge deployment — протилежність хмари: модель працює на пристрої чи локальному сервері, найближчому до того, де дані генеруються, а не у віддаленому дата-центрі. Причини: латенсі, вартість каналу, приватність (медичні дані не можуть залишати будівлю), офлайн-робота. PowerNodes від PAI3 — це edge deployment. Jetson, Raspberry Pi, Apple Silicon ноути — все edge-залізо."},
    "model-weight": {"term": "ваги моделі", "short": "Мільярди чисел усередині натренованої нейромережі. Те, що ти реально завантажуєш, коли «береш модель».", "long": "Ваги моделі — це параметри, вивчені під час тренування. Для 7B моделі — 7 мільярдів float-чисел. Це те, що робить модель «моделлю». Зберігаються як файли GGUF / safetensors / PyTorch `.bin`. Квантизація змінює, як ці числа зберігаються (16-біт, 4-біт і т.д.), але не те, що вони семантично представляють."},
    "token": {"term": "токен", "short": "Атомарна одиниця, яку LLM читає і пише. ~4 символи англійської. ~0.75 слова. «Слово» мови LLM.", "long": "LLM не читає символи чи слова — вона читає токени. Токен — це приблизно 4 символи англійського тексту, або близько ¾ слова. «Hello world» = 2 токени. Вікна контексту вимірюються у токенах (8K, 32K, 128K). Ціни API — за токени. Швидкість генерації — токени/секунду. Використання пам'яті росте з кількістю токенів у контексті."},
    "context-window": {"term": "context window", "short": "Скільки тексту модель може бачити за раз. 8K = короткий документ. 128K = ціла книга. Робоча пам'ять моделі.", "long": "Context window — максимум токенів, до яких модель може «доступитися» одночасно. Старі моделі: 2K-4K. Сучасні опенсорс: 8K-32K. Фронтирні: 128K-1M. Більший контекст = більше пам'яті, повільніший inference на токен. Для RAG: розмір чанка має комфортно влізати в context window."},
    "evaluation": {"term": "evaluation", "short": "Вимірювання, наскільки модель добра у задачі. «Eval set» = тест-кейси. «Eval harness» = раннер.", "long": "Evaluation (evals) — це спосіб дізнатися, чи дотренована модель реально краща за базову. Збираєш labelled test set (вхід → очікуваний вихід), запускаєш обидві моделі, порівнюєш скор. Категорії: multiple choice (MMLU), код (HumanEval), чат (MT-Bench), domain-specific (власний медичний Q&A set). Складна частина — зібрати якісний, не-leaking eval set."},
    "hallucination": {"term": "галюцинація", "short": "Модель впевнено каже щось неправдиве. Головний режим відмов LLM. RAG і grounding зменшують це.", "long": "Галюцинація — коли LLM генерує правдоподібно-звучний, але фактично хибний контент — вигадані цитати, фейкові API, вигадана статистика. Причина — модель натренована «звучати правильно», а не «бути правильною». Засоби: RAG-grounding, confidence threshold, post-generation fact-check, structured outputs, що вимагають цитат."},
    "fine-tuning": {"term": "fine-tuning", "short": "Продовження тренування базової моделі на своїх даних. Робить модель кращою у конкретній задачі.", "long": "Fine-tuning бере pre-trained базову модель і тренує її далі на меншому, task-specific датасеті. Результат — модель, що краща у твоїй задачі, але гірша в нерелевантних. LoRA / QLoRA — parameter-efficient версії, що додають крихітні адаптери замість перетренування всього. Порівняно з промптингом: промптинг скеровує модель під час інференсу, fine-tuning змінює її ваги."},
    "distillation": {"term": "distillation", "short": "Тренування маленької моделі наслідувати велику. «Вчитель відповідає, учень вчиться». Дешевше, ніж тренувати з нуля.", "long": "Knowledge distillation: велика «вчительська» модель (напр. GPT-4) генерує тренувальні дані, маленька «учнівська» модель вчиться їх імітувати. Результат: модель у 10 разів менша, що зберігає 80-90% якості вчителя на цільовій задачі. Поширено для деплою на edge-залізі — GPT-4 не запустиш на Jetson, а Mistral-7B, дистильований з нього — можна."},
    "rag-pipeline": {"term": "RAG-пайплайн", "short": "Весь шлях: нарізати документи → ембеди → скласти у векторну БД → на запит: ембеди запит → витягнути → промпт у LLM.", "long": "RAG-пайплайн має дві половини. Індексація (офлайн): різати документи на чанки (200-1000 токенів), ембедити кожен чанк, скласти у pgvector / Pinecone. Запит (онлайн): ембедити питання користувача, знайти top-k схожих чанків, покласти їх у промпт, попросити LLM відповідати лише на їх основі. Якість залежить від стратегії чанкінгу, embedding-моделі, методу retrieval і дизайну промпту."},
    "embedding-model": {"term": "embedding-модель", "short": "Модель, чия робота — перетворювати текст на вектор. Використовується для RAG retrieval, пошуку, кластеризації. Відрізняється від chat-моделі.", "long": "Embedding-моделі (напр. `text-embedding-3-small`, `bge-large`, `nomic-embed-text`) перетворюють текст у вектори фіксованої довжини так, що схожі тексти дають схожі вектори. Менші і швидші за chat-моделі — хорошу embedding-модель можна запустити локально. Вибирай ту, що підходить для твоєї мови і домену."},
    "context-window-budget": {"term": "context budget", "short": "Як розділити context window моделі: системний промпт vs. витягнуті документи vs. історія чату vs. питання користувача.", "long": "8K context window — не нескінченний. Треба вирішити: скільки токенів на системний промпт? Скільки на витягнуті RAG-чанки? Скільки на історію розмови? Скільки на питання користувача + очікувану відповідь? Поширений патерн: system (1K) + історія (2K) + retrieved (3K) + питання (1K) + буфер відповіді (1K) = 8K."},
    "secure-by-default": {"term": "secure by default", "short": "Система безпечна, якщо її використовувати рівно як задокументовано. Без «opt-in security» — дефолти відхиляють поганий кейс.", "long": "Secure by default означає, що конфіг з коробки відхиляє небезпечні операції. Приклад: chat-асистент, який за замовчуванням відмовляється викликати зовнішні API, редагує PII і валідує URL. Користувач може послабити, але дефолт безпечний. Протилежність — «opt-in security», де треба пам'ятати увімкнути guardrails, і хтось завжди забуває."},
    "idempotent": {"term": "ідемпотентний", "short": "Подвійний виклик операції дає той самий результат, що й одинарний. Критично для retries і безпеки webhook.", "long": "Ідемпотентна операція безпечна для retry: `POST /charge $10` (не ідемпотентна — подвійне списання) проти `POST /charge-idempotency-key=abc $10` (ідемпотентна — сервер пам'ятає і повертає оригінальний результат). Для agent-workflow retries на транзитні збої (timeout, мережа) неминучі — кожен зовнішній виклик має бути спроєктований ідемпотентним."},
    "webhook": {"term": "webhook", "short": "HTTP-колбек. Сервіс A POST-ить на твій URL, коли щось сталося. Альтернатива полінгу.", "long": "Webhook — це коли сервіс A надсилає HTTP POST на URL, який ти контролюєш, коли трапляється подія (новий email, нове замовлення, нове повідомлення). Твій сервер відповідає 200 OK, аби підтвердити. Протилежність полінгу — замість питати «є щось нове?» 100 разів/сек, чекаєш, поки тобі скажуть. Використовують Stripe, GitHub, Telegram, n8n."},
    "postgres": {"term": "PostgreSQL", "short": "Дефолтна серйозна open-source реляційна БД. З розширенням pgvector також слугує векторною БД.", "long": "PostgreSQL — open-source реляційна БД, обрана для продакшен-систем. ACID-транзакції, JSON-колонки, full-text search, екосистема розширень. Для AI-застосунків розширення `pgvector` додає векторний схожий пошук — одна БД для реляційних і embedding-даних, одна стратегія бекапу, один шар транзакцій."},
    "kubernetes-operator": {"term": "operator", "short": "Кастомний Kubernetes-контролер, що автоматизує життєвий цикл складного застосунку. PAI3 явно уникає цілої екосистеми.", "long": "Kubernetes-operators кодують знання людського оператора у софт, що працює in-cluster (напр. «etcd operator», що керує бекапом, апгрейдом, скейлінгом). Потужно, але потребує самого K8s, який PAI3 радить уникати. Філософія PAI3: bare metal + systemd + проста оркестрація, а не контейнери-на-K8s."},
    "ai-first-engineering": {"term": "AI-first engineering", "short": "Побудова софту, де AI є частиною самого робочого процесу команди, не лише продукту. Cursor + Claude для написання коду.", "long": "AI-first engineering означає, що сам процес розробки використовує AI як первинний інструмент: Cursor чи Claude Code для написання/редагування, LLM для рев'ю і генерації тестів, агенти для рутинного рефакторингу. PAI3 конкретно каже: «Використовуйте Cursor і Claude для побудови систем. Працюйте в AI-first engineering моделі.» Це мета-шар над продуктовим AI."},
    "decoded-inference": {"term": "інференс", "short": "Запуск натренованої моделі на нових вхідних даних для отримання виходу. Фаза «використання» ML, на противагу «тренуванню».", "long": "Інференс — це forward pass: береш натреновану модель, даєш їй вхід (промпт), отримуєш вихід (completion). Для LLM це генерація токен за токеном. Продакшен-інференс — це більшість обчислень ML: тренування відбувається один раз, інференс — мільярди разів. Фокус PAI3: зробити інференс надійним, швидким і приватним на локальних PowerNodes."},
    "deterministic": {"term": "детерміністичний", "short": "Однаковий вхід завжди дає однаковий вихід. Легко тестувати. Вихід LLM НЕ детерміністичний — це і є виклик.", "long": "Детерміністичний = відтворюваний: f(x) завжди повертає те саме f(x). Більшість коду детерміністична. LLM — ні за замовчуванням (sampling temperature > 0). Для тестування зазвичай ставлять temperature = 0, аби зробити вихід LLM детерміністичним, але продакшен-агенти часто потребують деякої недетерміністичності для обробки різноманітних входів."},
    "soak-test": {"term": "soak test", "short": "Прогон системи при нормальному навантаженні годинами/днями. Ловить memory leaks, повільний drift і збої, що з'являються з часом.", "long": "Soak test запускає систему під реалістичним навантаженням тривалий час (години чи дні). Ловить баги, яких не показують 5-хвилинні smoke-тести: memory leaks (RAM росте з часом), виснаження ресурсів (file descriptors, DB connections), повільний drift у поведінці моделі, log-файли забивають диск. Для AI-систем це критично — LLM memory leaks у KV cache можуть проявитися лише за години."},
}


# ============================================================================
# GLOSSARY — every term that must have a hover tooltip.
# Each entry: id -> {term (display EN, used for matching prose),
#                    short (one-line tooltip EN), long (modal body EN)}.
# The 'term' field stays English so the regex in render_qa_html() still matches
# surface forms that appear inside EN prose. For the UA page, prose shows the
# Ukrainian term via a separate display_ua override.
# ============================================================================

GLOSSARY = {
    # Core vacancy terms
    "pai3": {
        "term": "PAI3 Network",
        "short": "Decentralized AI network where all inference runs locally — no cloud, no central control. Goal: private AI for regulated environments.",
        "long": "PAI3 Network is a decentralized AI network designed for use cases where data privacy, local control, and offline operation matter more than raw scale. Their stack targets PowerNodes (edge hardware) and rejects cloud dependencies. Medical-software / intranet deployment is a typical target — patient data never leaves the local network."
    },
    "powernode": {
        "term": "PowerNode",
        "short": "Edge hardware node that runs AI inference locally inside the customer network. The physical machine where the model lives.",
        "long": "A PowerNode is PAI3's edge-compute appliance: a physical (or virtual) machine inside the customer's intranet that hosts the local LLM, the agent runtime, and any associated services. PowerNodes are managed as a fleet — updates, model rollouts, and health checks are pushed to each node individually. The 'decentralized' part of PAI3 means there is no central inference cluster; each PowerNode runs the model itself."
    },
    "intranet": {
        "term": "intranet",
        "short": "A private network inside one organization. No public internet exposure. The model never reaches outside this boundary.",
        "long": "An intranet is a closed network that only the organization's own users and devices can reach. For medical software this is critical: patient data, prompts, and model outputs must never leave the hospital or clinic's own network. The opposite of SaaS — no multi-tenant cloud, no shared infrastructure."
    },

    # Local inference / models
    "ollama": {
        "term": "Ollama",
        "short": "Tool that runs LLMs locally as a simple HTTP server. Pulls pre-trained models, exposes an OpenAI-compatible API on localhost.",
        "long": "Ollama is a developer-friendly local-LLM runtime. You `ollama pull mistral` once and then have a model serving completion requests on `http://localhost:11434`. It handles model download, quantization defaults (Q4_K_M), GPU/CPU fallback, and exposes an OpenAI-shaped API so application code doesn't need to change when switching between cloud and local inference."
    },
    "gguf": {
        "term": "GGUF",
        "short": "File format for quantized LLMs (GPT-Generated Unified Format). What Ollama / llama.cpp actually load off disk.",
        "long": "GGUF is the modern successor to GGML. It is a single-file format that bundles the model weights, tokenizer, and metadata in a way that mmap-loads quickly. Different quantization levels live in the same family: Q2_K (smallest, weakest), Q4_K_M (the common sweet spot), Q6_K, Q8_0. The trade-off is memory vs quality — smaller files fit on weaker hardware but the model is a bit dumber."
    },
    "quantization": {
        "term": "quantization",
        "short": "Shrinking a model by storing weights in fewer bits (e.g. 16-bit → 4-bit). Saves 3-4× memory at a small quality cost.",
        "long": "Quantization reduces the precision of each weight from 16-bit or 32-bit floating point down to 4-bit, 8-bit, etc. The model disk size and RAM footprint drop dramatically (4-bit = ~4× smaller) and inference gets faster, with a small loss in output quality. Common formats: GGUF, GPTQ, AWQ, bitsandbytes (4-bit). For edge hardware (8-16 GB RAM), quantization is what makes running a 7B-13B model possible."
    },
    "q4-k-m": {
        "term": "Q4_K_M",
        "short": "A specific 4-bit GGUF quantization level. The default sweet spot — small, fast, ~99% of full quality on most tasks.",
        "long": "Q4_K_M is one of the k-quant variants in GGUF. The 'Q4' means 4-bit weights, 'K' means the k-quant method (mixed-precision per layer), 'M' is medium (between Q4_K_S smaller and Q4_K_L larger). It is the most common default in Ollama because the quality loss vs full precision is small for typical chat/RAG tasks, while the size is ~4 GB for a 7B model."
    },
    "lora": {
        "term": "LoRA",
        "short": "Low-Rank Adaptation. A small trainable 'patch' added on top of a frozen base model. Cheap to train, cheap to swap.",
        "long": "LoRA fine-tunes a model by inserting two small trainable matrices into each transformer layer, while keeping the original weights frozen. The result is a tiny adapter file (often <100 MB) that captures the new behaviour. You can have dozens of LoRAs for different tasks and load the right one at inference time without copying the whole base model."
    },
    "qlora": {
        "term": "QLoRA",
        "short": "LoRA combined with 4-bit quantization of the base model. Trains adapters on a model that fits in consumer GPU memory.",
        "long": "QLoRA = quantized base + LoRA adapter. The base model is loaded in 4-bit (via bitsandbytes), so it fits in 16-24 GB of VRAM. Then small LoRA adapters are trained on top. This is what makes fine-tuning a 7B-13B model possible on a single consumer GPU instead of a multi-A100 cluster."
    },
    "pytorch": {
        "term": "PyTorch",
        "short": "The dominant Python framework for training and running neural networks. The standard tool for any custom model work.",
        "long": "PyTorch is the de-facto framework for deep learning research and production training. Almost every open-source model (LLaMA, Mistral, Stable Diffusion) ships with PyTorch weights and PyTorch training code. For LoRA/QLoRA fine-tuning, the canonical stack is PyTorch + Hugging Face Transformers + PEFT + bitsandbytes."
    },
    "peft": {
        "term": "PEFT",
        "short": "Parameter-Efficient Fine-Tuning. Hugging Face library that implements LoRA / QLoRA / adapters on top of any base model.",
        "long": "PEFT (Hugging Face) is the standard library for parameter-efficient fine-tuning. It wraps any base model and adds small trainable adapters (LoRA, IA3, prefix-tuning) without touching the frozen weights. Combined with `bitsandbytes` for 4-bit loading, it is the canonical recipe for fine-tuning a 7B+ model on a single GPU."
    },
    "bitsandbytes": {
        "term": "bitsandbytes",
        "short": "Python library that gives you 4-bit / 8-bit quantized model loading in PyTorch. Used together with PEFT for QLoRA.",
        "long": "bitsandbytes (bnb) provides 4-bit and 8-bit quantization primitives for PyTorch. The `BitsAndBytesConfig` lets a Hugging Face model load in 4-bit NF4 with double quantization, dropping memory by ~4×. This is the foundation that QLoRA is built on."
    },
    "transformer": {
        "term": "transformer",
        "short": "The neural-network architecture behind modern LLMs. Self-attention layers stacked 32-80+ deep. The 'T' in GPT.",
        "long": "The transformer architecture (Vaswani et al., 2017) is the foundation of nearly all modern LLMs. It uses self-attention — every token looks at every other token in the context window — stacked in many layers. Each layer has attention heads and a feed-forward block. Fine-tuning typically modifies adapter weights in attention layers, not the feed-forward blocks."
    },

    # Agent orchestration
    "langchain": {
        "term": "LangChain",
        "short": "Python / TypeScript framework for chaining LLM calls, tools, and memory. The most common LLM application framework.",
        "long": "LangChain provides abstractions for prompts, tools, retrievers, memory, and chains — the building blocks of an LLM application. As of 2024-2025 it is being superseded for stateful agent work by LangGraph, but remains the standard for simpler RAG and tool-use pipelines."
    },
    "langgraph": {
        "term": "LangGraph",
        "short": "Stateful, graph-based agent framework from the LangChain team. Each agent is a node, transitions are edges, state is explicit.",
        "long": "LangGraph models an agent system as a directed graph: nodes are functions (LLM calls, tool invocations, human approval steps), edges are transitions (conditional or fixed), and a shared typed `State` object flows through the graph. It supports checkpointing (resume after crash), cycles, and human-in-the-loop interrupts. The successor to LangChain for serious multi-agent work."
    },
    "rag": {
        "term": "RAG",
        "short": "Retrieval-Augmented Generation. The model answers questions using text chunks pulled from a vector database at query time.",
        "long": "RAG is the dominant pattern for grounding LLMs in private / fresh data. At query time, the user's question is embedded into a vector, similar chunks are retrieved from a vector database (pgvector, Pinecone, Weaviate), and those chunks are stuffed into the prompt as context. The model then answers grounded in those chunks, not just its training data. Reduces hallucination and lets you cite sources."
    },
    "pgvector": {
        "term": "pgvector",
        "short": "Postgres extension that adds vector similarity search to a normal Postgres table. RAG without a separate vector DB.",
        "long": "pgvector adds a `vector` column type and ANN (approximate nearest neighbour) indexes (HNSW, IVFFlat) to PostgreSQL. For teams that already run Postgres, this is the simplest path to RAG — embeddings live next to the relational data, one transaction layer, one backup story. Trade-off: at millions of vectors, dedicated vector DBs (Pinecone, Qdrant) scale better."
    },
    "vector-embedding": {
        "term": "embedding",
        "short": "A list of numbers (e.g. 1536 floats) that represents the meaning of a text. Similar texts → similar vectors.",
        "long": "An embedding is a fixed-length dense vector produced by a model (e.g. OpenAI `text-embedding-3-small` outputs 1536 floats). Semantically similar texts produce vectors that are close in cosine distance. Used for semantic search, RAG retrieval, clustering, and classification."
    },
    "cosine-similarity": {
        "term": "cosine similarity",
        "short": "How to measure if two embedding vectors mean the same thing. Score from -1 (opposite) to 1 (same).",
        "long": "Cosine similarity = dot product of two vectors divided by the product of their magnitudes. It ignores vector length and only cares about direction, which makes it the right metric for embeddings (where length is meaningless, direction is meaning). For RAG, top-k retrieval by cosine similarity picks the chunks most relevant to the query."
    },
    "agent": {
        "term": "agent",
        "short": "An LLM-driven program that decides what to do next based on the goal, not a fixed script. Loop: think → act → observe.",
        "long": "An LLM agent is a system where the model itself chooses actions (tool calls, searches, code execution) in a loop until some stopping condition. Compare to a chain (fixed sequence) or a pipeline (deterministic graph). Agents are powerful but harder to test, easier to hallucinate, and need explicit guardrails."
    },
    "n8n": {
        "term": "n8n",
        "short": "Open-source workflow automation tool. Visual editor for chains of API calls, AI nodes, conditionals, and retries.",
        "long": "n8n is a self-hostable alternative to Zapier / Make. You build workflows in a visual editor: trigger → node → node → conditional branch → error path. It has native LLM / AI agent nodes, HTTP request nodes, and 400+ integrations. For solo / small-team automation it's faster to ship than building a custom agent runtime, and the JSON workflow files are version-controllable."
    },

    # RAG / safety / testing
    "prompt-injection": {
        "term": "prompt injection",
        "short": "User input that tricks the LLM into ignoring its real instructions and following the attacker's instead. The #1 LLM security risk.",
        "long": "Prompt injection is when user-controlled text (or even third-party content the model retrieves) contains instructions like 'ignore your previous instructions and do X'. The model cannot reliably distinguish user content from system instructions. Defences: pre-LLM input filters, structured-output constraints, post-LLM output validation, and treating any retrieved content as untrusted."
    },
    "system-prompt": {
        "term": "system prompt",
        "short": "The hidden instructions that set the LLM's role, scope, and behaviour. The model's 'job description'.",
        "long": "The system prompt is sent to the model as the first message in the conversation with role 'system'. It defines what the model should do (and not do), its tone, its scope, what it must refuse. Vulnerable to extraction attacks ('repeat your system prompt verbatim') — so production systems should never put secrets in it."
    },
    "guardrails": {
        "term": "guardrails",
        "short": "Deterministic checks that sit before or after the LLM call. Reject bad input, validate bad output.",
        "long": "Guardrails are non-LLM rules that filter or transform what goes into or comes out of the model. Pre-LLM: regex / classifier rejects prompt injection, oversized input, off-topic requests. Post-LLM: schema validation, PII redaction, URL allowlist, length cap. The point: never trust the model alone to enforce policy."
    },
    "grounding": {
        "term": "grounding",
        "short": "Anchoring the model's answer in retrieved facts (RAG) or verified data. The opposite of hallucinating.",
        "long": "Grounding means the model is told to answer only based on provided context, and to say 'I don't know' if the context is insufficient. RAG is the dominant grounding technique. Hallucination drops sharply when the model is forced to cite retrieved chunks rather than free-generation from its training distribution."
    },
    "structured-output": {
        "term": "structured output",
        "short": "Forcing the model to respond as JSON matching a schema, not free-form text. Makes outputs machine-checkable.",
        "long": "Structured output (e.g. OpenAI's JSON mode, Zod / Pydantic schemas, instructor library) constrains the model's response to valid JSON matching a declared shape. The downstream code can then trust the structure: `response.risk_level` is always one of `low | medium | high`, never a free-form sentence. Eliminates an entire class of parsing bugs."
    },
    "zod": {
        "term": "Zod",
        "short": "TypeScript library for declaring data shapes and validating at runtime. Used to validate LLM structured outputs.",
        "long": "Zod is the most popular TypeScript schema validation library. You write `z.object({ name: z.string(), age: z.number().int().positive() })` and Zod both infers the TypeScript type and validates any runtime data against it. In LLM pipelines, Zod is the typical way to define and enforce the shape of structured model outputs."
    },
    "confidence-threshold": {
        "term": "confidence threshold",
        "short": "The minimum retrieval score below which the assistant refuses to answer instead of guessing.",
        "long": "When RAG retrieves context chunks, each chunk has a similarity score. A confidence threshold is the cut-off: chunks above the threshold are considered 'the model has enough context to answer', below means 'context is too weak, refuse or escalate'. Tuning this threshold trades false refusals against hallucinated answers."
    },

    # Infra / deployment
    "docker": {
        "term": "Docker",
        "short": "Packages an app + its dependencies into a single runnable container. Same behaviour on any Linux host.",
        "long": "Docker uses OS-level virtualization to package an application with its libraries, configs, and runtime into a container image. The image runs identically on a developer laptop, a CI server, or a production node. For AI inference you typically containerize the model server (Ollama, vLLM, TGI) so deployments are reproducible."
    },
    "kubernetes": {
        "term": "Kubernetes",
        "short": "Container orchestrator. Manages hundreds of containers across many machines. Heavy infrastructure.",
        "long": "Kubernetes (K8s) is the industry-standard orchestrator for running containerised workloads at scale: scheduling, self-healing, rolling updates, service discovery. Powerful but heavy — requires a control plane, networking layer, ingress controllers. PAI3 explicitly avoids it: 'Do not rely on Kubernetes, Docker, or cloud pipelines'."
    },
    "cloudflare-tunnel": {
        "term": "Cloudflare Tunnel",
        "short": "A secure outbound tunnel that exposes a local service to the internet without opening firewall ports.",
        "long": "Cloudflare Tunnel (`cloudflared`) runs as a process on your machine and opens an outbound-only connection to Cloudflare's edge. You then get a public HTTPS URL that proxies into your local service. No inbound firewall rules, no public IP needed. Useful for exposing a self-hosted n8n or portfolio demo without port-forwarding."
    },
    "tailscale": {
        "term": "Tailscale",
        "short": "Mesh VPN that connects your devices into a private network using WireGuard. Zero-config, identity-based.",
        "long": "Tailscale builds a WireGuard mesh VPN between your devices (laptop, server, phone) using your existing identity (Google, GitHub, Microsoft login). No port forwarding, no firewall rules. Each device gets a stable IP on the tailnet (100.x.y.z). For ops work it's the fastest way to reach a homelab server from anywhere."
    },
    "coolify": {
        "term": "Coolify",
        "short": "Self-hosted PaaS. Deploy apps and databases from a web UI without Kubernetes. 'Heroku on your own server'.",
        "long": "Coolify is an open-source self-hostable platform-as-a-service. It manages Docker containers, databases, SSL via Let's Encrypt, and reverse proxy via Traefik — all from a web UI. For solo developers or small teams it replaces Vercel / Fly.io / Heroku with a homelab-friendly alternative that doesn't require Kubernetes."
    },
    "systemd": {
        "term": "systemd",
        "short": "Linux service manager. Starts your app on boot, restarts on crash, writes logs. The 'start.sh' of production Linux.",
        "long": "systemd is the default init system on modern Linux. You write a `.service` unit file describing how to run your app, then `systemctl enable --now myapp` makes it start on boot and auto-restart on failure. For non-Docker local deployments (PAI3's preferred style), systemd is the equivalent of a Docker restart policy."
    },

    # Observability / governance
    "observability": {
        "term": "observability",
        "short": "Being able to understand what your system is doing from its outputs — logs, metrics, traces. Required for debugging AI in production.",
        "long": "Observability is the discipline of making a system's internal state understandable from its external outputs. The three pillars are logs (discrete events), metrics (aggregated numbers over time), and traces (a request's path across services). For AI systems you also need prompt/response logs, retrieval scores, and confidence distributions — the LLM is non-deterministic so traditional debugging doesn't apply."
    },
    "metrics": {
        "term": "metrics",
        "short": "Numbers that summarise system behaviour over time. Request rate, error rate, p99 latency. Grafana dashboards.",
        "long": "Metrics are scalar time-series values: requests per second, error rate, latency percentiles, GPU utilisation, tokens per second. Stored in Prometheus or similar. For AI: token usage, retrieval confidence distribution, model refusal rate."
    },
    "logging": {
        "term": "logging",
        "short": "Writing timestamped events to a file or service. The 'what happened' record of your system.",
        "long": "Logs are append-only event records: `[2026-09-18 16:01:23] POST /api/inference 200 1.4s model=mistral-7b-q4`. For AI systems you should log prompt, response, retrieved chunks, and confidence — but be careful with PII and secrets. Structured JSON logs (one event per line) are easier to query than plain text."
    },
    "governance": {
        "term": "governance",
        "short": "The rules, roles, and review processes that decide who can do what to a system. Especially important for AI that affects real people.",
        "long": "Governance is the layer above the code: who can deploy, who can approve a model change, what data is allowed, what the review process is for incidents. For medical AI this becomes regulation: HIPAA, MDR, audit trails, model change records, rollback procedures. 'Governance' here means the human + policy layer, not the LLM."
    },
    "hipaa": {
        "term": "HIPAA",
        "short": "US healthcare privacy law. Governs how patient data must be handled. Software touching patient data must comply.",
        "long": "Health Insurance Portability and Accountability Act (1996). Sets rules for protected health information (PHI): who can see it, how it must be stored, breach notification, audit logs. Any software that processes patient data — including an LLM-based assistant that reads clinical notes — must be designed with HIPAA in mind."
    },
    "phi": {
        "term": "PHI",
        "short": "Protected Health Information. Any data that identifies a patient and relates to their health. Handle with care.",
        "long": "PHI is the legal term for any individually identifiable health data: name + diagnosis, MRN, date of birth + visit, even IP address when combined with health info. Sending PHI to a third-party API (including an LLM API) without a Business Associate Agreement is a HIPAA violation. Drives why medical AI runs locally."
    },
    "audit-trail": {
        "term": "audit trail",
        "short": " Immutable record of who did what and when. Required for regulated industries (health, finance).",
        "long": "An audit trail is a tamper-evident log of every action in the system: who accessed what data, who changed which setting, who deployed which model version. For regulated AI (medical, financial), audit trails are non-negotiable — they are what you show regulators when something goes wrong."
    },
    "human-in-the-loop": {
        "term": "human-in-the-loop",
        "short": "A human must approve or correct the AI's output before it takes effect. Pattern for high-stakes decisions.",
        "long": "Human-in-the-loop (HITL) is a workflow where the AI proposes an action or answer, but a human reviews and approves before anything irreversible happens. Standard in medical AI: the model drafts a summary, the clinician signs off. LangGraph supports this natively via interrupt nodes."
    },
    "rollback": {
        "term": "rollback",
        "short": "Reverting a system to a previous known-good version. The safe button when a new model or deploy breaks things.",
        "long": "Rollback is the ability to quickly return to a previous working state. For AI models: keep old checkpoints, version your adapters, have a tested procedure to swap back. For deployments: keep the previous container image, use blue/green or canary releases. The difference between an incident and a catastrophe is whether rollback takes 30 seconds or 30 hours."
    },
    "checkpoint": {
        "term": "checkpoint",
        "short": "A saved snapshot of a model or workflow state. Resuming training, recovering after crash, or rolling back.",
        "long": "A checkpoint is a persisted snapshot. For model training: saved weights at step N (so you can resume if it crashes). For LangGraph workflows: the current state of every node (so a multi-hour agent run can resume after a server restart). For inference: a frozen model version you can roll back to."
    },
    "blue-green": {
        "term": "blue/green",
        "short": "Deploy by running new and old versions side by side, then swapping traffic. Zero-downtime, instant rollback.",
        "long": "Blue/green deployment: run the current version ('blue') and the new version ('green') simultaneously. Route all traffic to blue. Test green in production. When green is verified, flip the load balancer to green. If green breaks, flip back to blue — instant rollback, no rush to debug under pressure."
    },
    "load-balancer": {
        "term": "load balancer",
        "short": "A server that distributes incoming requests across multiple backends. The entry door of a scalable service.",
        "long": "A load balancer (NGINX, HAProxy, Cloudflare, AWS ALB) accepts inbound traffic and forwards each request to one of N backend instances. Distributes load, provides failover (if one backend dies, send to the rest), and enables zero-downtime deployments (blue/green). For AI: route to the PowerNode with the lowest current load."
    },

    # Domain — production AI
    "p99": {
        "term": "p99 latency",
        "short": "The slowest 1% of requests. The real 'user experience' number — p50 lies, p99 doesn't.",
        "long": "p99 latency is the 99th percentile: 99% of requests finish faster than this, only 1% are slower. p50 (median) hides the worst cases. For AI: p99 includes the cold-start of the first request after idle, the slow token on a long context, the timeout retry. Production SLOs are usually written against p99."
    },
    "throughput": {
        "term": "throughput",
        "short": "How many requests (or tokens) per second the system can handle. Capacity, not speed.",
        "long": "Throughput is the rate of completed work: requests/second, tokens/second, inferences/hour. For LLM serving: tokens per second per GPU. Different from latency — a system can be fast (low latency) but low-throughput (small batch size, runs out of GPU memory) or high-throughput but slow per-request. For medical assistants, throughput matters more than peak speed."
    },
    "tokens-per-second": {
        "term": "tokens/sec",
        "short": "How fast the model generates output. ~30 tok/s = readable, ~100 tok/s = instant. The user-visible speed metric.",
        "long": "LLMs generate text one token at a time (~4 chars in English). Tokens per second is the user-visible speed of the model. On a 7B model with Q4 quantization on a modern GPU: 50-100 tok/s. On CPU: 5-15 tok/s. For chat UX you want at least 30 tok/s; below that the response feels sluggish."
    },
    "edge-deployment": {
        "term": "edge deployment",
        "short": "Running the model close to the data (laptop, hospital server, IoT device) instead of in a central cloud.",
        "long": "Edge deployment is the opposite of cloud: the model runs on the device or local server nearest to where the data is generated, not in a distant data centre. Reasons: latency, bandwidth cost, privacy (medical data can't leave the building), offline operation. PAI3's PowerNodes are edge deployment. Jetson, Raspberry Pi, Apple Silicon laptops — all edge hardware."
    },
    "model-weight": {
        "term": "model weights",
        "short": "The billions of numbers inside a trained neural network. What you actually download when you 'get a model'.",
        "long": "A model's weights are the parameters learned during training — for a 7B model, 7 billion floating-point numbers. They are what makes the model 'the model'. Stored as GGUF / safetensors / PyTorch `.bin` files. Quantization changes how those numbers are stored (16-bit, 4-bit, etc.) but not what they semantically represent."
    },
    "token": {
        "term": "token",
        "short": "The atomic unit an LLM reads and writes. ~4 characters of English. ~0.75 words. The 'word' of an LLM.",
        "long": "An LLM doesn't read characters or words — it reads tokens. A token is roughly 4 characters of English text, or about ¾ of a word. 'Hello world' = 2 tokens. Context windows are measured in tokens (8K, 32K, 128K). API costs are per-token. Generation speed is tokens/second. Memory usage scales with tokens in context."
    },
    "context-window": {
        "term": "context window",
        "short": "How much text the model can see at once. 8K = a short doc. 128K = a whole book. The model's working memory.",
        "long": "The context window is the maximum number of tokens the model can attend to at once. Older models: 2K-4K. Modern open models: 8K-32K. Frontier models: 128K-1M. Bigger context = more memory, slower per-token inference. For RAG: chunk size must fit comfortably inside the context window."
    },
    "evaluation": {
        "term": "evaluation",
        "short": "Measuring how good a model is at a task. 'Eval set' = the test cases. 'Eval harness' = the runner.",
        "long": "Evaluation (evals) is how you know if a fine-tuned model is actually better than the base. You build a labelled test set (input → expected output), run both models, compare scores. Categories: multiple choice (MMLU), code (HumanEval), chat (MT-Bench), domain-specific (your own medical Q&A set). The hard part is building a high-quality, non-leaking eval set."
    },
    "hallucination": {
        "term": "hallucination",
        "short": "The model confidently stating something false. The core LLM failure mode. RAG and grounding reduce it.",
        "long": "Hallucination is when the LLM generates plausible-sounding but factually wrong content — invented citations, fake APIs, made-up statistics. Caused by the model being trained to 'sound right' rather than 'be right'. Mitigations: RAG grounding, confidence thresholds, post-generation fact-checking, structured outputs that require citations."
    },
    "fine-tuning": {
        "term": "fine-tuning",
        "short": "Continuing training of a base model on your own data. Makes the model better at your specific task.",
        "long": "Fine-tuning takes a pre-trained base model and trains it further on a smaller, task-specific dataset. The result is a model that is better at your task but worse at unrelated things. LoRA / QLoRA are parameter-efficient versions that add tiny adapters instead of retraining everything. Compared to prompting: prompting steers a model at inference, fine-tuning changes its weights."
    },
    "distillation": {
        "term": "distillation",
        "short": "Training a small model to mimic a big one. 'Teacher answers, student learns'. Cheaper than training from scratch.",
        "long": "Knowledge distillation: a large 'teacher' model (e.g. GPT-4) generates training data, a small 'student' model learns to mimic it. Result: a model 10× smaller that retains 80-90% of the teacher's quality on the target task. Common for deploying on edge hardware — you can't run GPT-4 on a Jetson, but you can run a Mistral-7B that was distilled from it."
    },
    "rag-pipeline": {
        "term": "RAG pipeline",
        "short": "The end-to-end flow: chunk docs → embed → store in vector DB → at query time, embed query → retrieve → prompt LLM.",
        "long": "A RAG pipeline has two halves. Indexing (offline): split documents into chunks (200-1000 tokens), embed each chunk, store in pgvector / Pinecone. Query (online): embed the user's question, find top-k similar chunks, stuff them into the prompt, ask the LLM to answer using only those chunks. Quality depends on chunking strategy, embedding model, retrieval method, and prompt design."
    },
    "embedding-model": {
        "term": "embedding model",
        "short": "A model whose job is to turn text into a vector. Used for RAG retrieval, search, clustering. Different from a chat model.",
        "long": "Embedding models (e.g. `text-embedding-3-small`, `bge-large`, `nomic-embed-text`) convert text into fixed-length dense vectors such that similar texts get similar vectors. Smaller and faster than chat models — you can run a good embedding model locally. Pick the right one for your language and domain."
    },
    "context-window-budget": {
        "term": "context budget",
        "short": "How you split the model's context window: system prompt vs. retrieved docs vs. chat history vs. user question.",
        "long": "An 8K context window is not infinite. You must decide: how many tokens for the system prompt? How many for retrieved RAG chunks? How much conversation history? How much for the user's question + expected answer? A common pattern: system (1K) + history (2K) + retrieved (3K) + question (1K) + answer buffer (1K) = 8K total."
    },
    "secure-by-default": {
        "term": "secure by default",
        "short": "The system is safe when used exactly as documented. No 'opt-in security' — defaults reject the bad case.",
        "long": "Secure by default means the configuration that ships out of the box rejects unsafe operations. Example: a chat assistant that, by default, refuses to call external APIs, redact PII, and validate URLs. Users can loosen it, but the default is safe. The opposite is 'opt-in security' where you must remember to enable the guardrails — and someone always forgets."
    },
    "idempotent": {
        "term": "idempotent",
        "short": "Calling an operation twice produces the same result as calling it once. Critical for retries and webhook safety.",
        "long": "An idempotent operation can be retried safely: `POST /charge $10` (not idempotent — double charge) vs `POST /charge-idempotency-key=abc $10` (idempotent — server remembers and returns the original result). For agent workflows, retries on transient failures (timeout, network) are unavoidable — every external call should be designed idempotently."
    },
    "webhook": {
        "term": "webhook",
        "short": "An HTTP callback. Service A POSTs to your URL when something happens. The alternative to polling.",
        "long": "A webhook is when service A sends an HTTP POST to a URL you control whenever an event occurs (new email, new order, new message). Your server responds with 200 OK to acknowledge. The opposite of polling — instead of asking 'is there anything new?' 100 times/sec, you wait to be told. Used by Stripe, GitHub, Telegram, n8n."
    },
    "postgres": {
        "term": "PostgreSQL",
        "short": "The default serious open-source relational database. With pgvector extension it also serves as a vector DB.",
        "long": "PostgreSQL is the open-source relational database of choice for production systems. ACID transactions, JSON columns, full-text search, extensions ecosystem. For AI applications the `pgvector` extension adds vector similarity search — one database for both relational and embedding data, one backup story, one transaction layer."
    },
    "kubernetes-operator": {
        "term": "operator",
        "short": "A custom Kubernetes controller that automates a complex application's lifecycle. PAI3 explicitly avoids this whole ecosystem.",
        "long": "Kubernetes operators encode human operator knowledge into software that runs in-cluster (e.g. an 'etcd operator' that handles backup, upgrade, scaling). Powerful but requires K8s itself, which PAI3 says to avoid. The PAI3 philosophy: bare metal + systemd + simple orchestration, not containers-on-K8s."
    },
    "ai-first-engineering": {
        "term": "AI-first engineering",
        "short": "Building software where AI is part of the team's workflow itself, not just the product. Cursor + Claude to write code.",
        "long": "AI-first engineering means the development process itself uses AI as a primary tool: Cursor or Claude Code for writing/editing, LLMs for review and test generation, agents for routine refactors. PAI3 specifically says 'Use Cursor and Claude to build systems. Operate in an AI-first engineering model.' This is the meta-layer above the product AI."
    },
    "decoded-inference": {
        "term": "inference",
        "short": "Running a trained model on new input to get output. The 'using' phase of ML, as opposed to 'training'.",
        "long": "Inference is the forward pass: take a trained model, give it an input (a prompt), get the output (a completion). For LLMs this is token-by-token generation. Production inference is the bulk of ML compute — training happens once, inference runs billions of times. PAI3's focus: making inference reliable, fast, and private on local PowerNodes."
    },
    "deterministic": {
        "term": "deterministic",
        "short": "Same input always gives the same output. Easy to test. LLM output is NOT deterministic — that's the whole challenge.",
        "long": "Deterministic means reproducible: f(x) always returns the same f(x). Most code is deterministic. LLMs are not by default (sampling temperature > 0). For testing, you typically set temperature = 0 to make LLM output deterministic, but production agents often need some non-determinism to handle varied inputs."
    },
    "soak-test": {
        "term": "soak test",
        "short": "Run the system at normal load for hours/days. Catches memory leaks, slow drift, and failures that only appear over time.",
        "long": "A soak test runs the system under realistic load for an extended period (hours to days). Catches bugs that don't show up in 5-minute smoke tests: memory leaks (RAM grows over time), resource exhaustion (file descriptors, DB connections), slow drift in model behaviour, log file filling disk. For AI systems this is critical — LLM memory leaks in the KV cache can take hours to manifest."
    },
}

# ============================================================================
# QUESTIONS + ANSWERS — single source of truth.
# Each entry: id, question (EN/UA), answer (EN/UA), category.
# Plain prose; technical terms are auto-linked to glossary via simple case-
# insensitive substring match. Terms are matched longest-first.
# ============================================================================

QUESTIONS = [
    {
        "id": 1,
        "cat_en": "Local Inference & Model Work",
        "cat_ua": "Локальна інференс та моделі",
        "q_en": "Have you deployed a model to run entirely locally in production, with no cloud API involved?",
        "q_ua": "Чи запускали ви модель повністю локально у продакшені, без жодного хмарного API?",
        "a_en": (
            "Yes. I run a self-hosted local inference path today at my current company. The architecture uses Ollama with a Mistral-family model "
            "on a self-hosted server — the request path is designed so that model inference itself does not depend on an external LLM API. "
            "The surrounding stack is n8n for workflow orchestration, Cloudflare Tunnel for controlled ingress, and self-hosted Postgres for data.\n\n"
            "My role is broader than 'start the model server'. I own the surrounding system: deployment, service boundaries, secrets handling, "
            "recovery procedures, documentation, and the operational setup that makes the path repeatable.\n\n"
            "I have also designed the target architecture for a larger local-LLM / RAG setup: Ollama-hosted models, PostgreSQL with pgvector, "
            "locally hosted embeddings, and clean separation between application, inference, and data layers.\n\n"
            "Honest scope: my strength is the local-inference system and operational architecture. I am not positioning myself as an inference-"
            "kernel or model-training specialist — those are the areas PAI3 would help me deepen."
        ),
        "a_ua": (
            "Так. Зараз у моїй компанії я підтримую self-hosted шлях локальної інференції. Архітектура — Ollama з моделлю родини Mistral "
            "на self-hosted сервері. Весь request path спроєктований так, що інференс моделі не залежить від зовнішнього LLM API.\n\n"
            "Навколо — n8n для оркестрації, Cloudflare Tunnel для контрольованого ingress, self-hosted Postgres для даних.\n\n"
            "Моя роль ширша за «запустити модель-сервер». Я відповідаю за оточуючу систему: деплой, межі сервісів, роботу з секретами, "
            "процедури відновлення, документацію, операційний сетап, який можна повторити.\n\n"
            "Я також спроєктував цільову архітектуру для більшого local-LLM / RAG: Ollama-моделі, PostgreSQL з pgvector, локальні embeddings, "
            "чисте розділення між application, inference і data шарами.\n\n"
            "Чесно: моя сила — це local-inference система і операційна архітектура. Я не позиціоную себе як фахівця з inference-ядра чи тренування "
            "моделей — це ті сфери, які я хочу поглибити разом з PAI3."
        ),
    },
    {
        "id": 2,
        "cat_en": "Local Inference & Model Work",
        "cat_ua": "Локальна інференс та моделі",
        "q_en": "This role involves PyTorch and LoRA / QLoRA fine-tuning work. What is your hands-on experience with these, if any?",
        "q_ua": "Ця роль передбачає PyTorch і LoRA / QLoRA fine-tuning. Який ваш практичний досвід з цим, якщо є?",
        "a_en": (
            "I have not shipped a LoRA / QLoRA fine-tune to production yet.\n\n"
            "What I know conceptually: freezing the base model, training adapter weights, 4-bit quantized bases for QLoRA via bitsandbytes, "
            "dataset preparation, evaluation, and rolling back to a base checkpoint if a fine-tune regresses.\n\n"
            "My production strength is the surrounding system: local inference, prompt and context engineering, RAG, evaluation logic, "
            "deployment, security, and operational architecture. That is what I have shipped.\n\n"
            "My ramp plan: start from a small reproducible experiment on a public base model, build the evaluation set first, then compare "
            "the fine-tuned checkpoint against the baseline. Not a 2-week promise — a 6-8 week honest ramp for production-grade fine-tuning."
        ),
        "a_ua": (
            "LoRA / QLoRA fine-tune у продакшен я ще не відправляв.\n\n"
            "Що знаю концептуально: заморозка базової моделі, тренування адаптерних ваг, 4-bit квантизована база для QLoRA через bitsandbytes, "
            "підготовка датасету, оцінка якості, відкат на базовий checkpoint якщо fine-tune став гіршим.\n\n"
            "Моя продакшен-сила — це оточуюча система: локальна інференс, prompt і context engineering, RAG, evaluation логіка, деплой, "
            "безпека, операційна архітектура. Це я вже відвантажив.\n\n"
            "Мій план ramp: почати з малого відтворюваного експерименту на публічній базовій моделі, спочатку побудувати eval-сет, потім "
            "порівняти fine-tuned checkpoint з базою. Не обіцянка «за 2 тижні» — чесний ramp 6-8 тижнів до production-grade fine-tuning."
        ),
    },
    {
        "id": 3,
        "cat_en": "Local Inference & Model Work",
        "cat_ua": "Локальна інференс та моделі",
        "q_en": "What is your experience with quantization (e.g. GGUF) for running models on constrained, edge-class hardware?",
        "q_ua": "Який ваш досвід з quantization (напр. GGUF) для запуску моделей на обмеженому edge-class залізі?",
        "a_en": (
            "Hands-on: deploying and operating pre-quantized GGUF models through Ollama, including Q4_K_M-class checkpoints. Selecting model "
            "sizes that fit available hardware, managing context window and memory constraints, picking CPU vs GPU allocation, and "
            "understanding the trade-off between model size, latency, memory use, and output quality.\n\n"
            "I am familiar with formats and approaches such as GGUF, GPTQ, AWQ and 4-bit quantization in general. What I have not done: "
            "personally built a quantization pipeline from a full-precision base model, or run a formal multi-quant perplexity benchmark on "
            "edge hardware. I have not yet shipped to Jetson / Raspberry Pi / mobile-class hardware.\n\n"
            "So my experience is strongest on the deployment and systems side of quantized local models. Going deeper into quantization "
            "internals and constrained-device benchmarking is an area I actively want to develop."
        ),
        "a_ua": (
            "Практично: деплоїв і експлуатував pre-quantized GGUF моделі через Ollama, включно з Q4_K_M-класом чекпоінтів. Вибирав розмір "
            "моделі під доступне залізо, працював з обмеженнями context window і пам'яті, розподілом CPU/GPU, розумів trade-off між розміром "
            "моделі, latency, споживанням пам'яті і якістю відповідей.\n\n"
            "Знайомий з форматами GGUF, GPTQ, AWQ, 4-bit quantization загалом. Чого не робив: не будував власноруч quantization pipeline з "
            "full-precision бази і не запускав формальний multi-quant perplexity бенчмарк на edge залізі. Не відправляв на Jetson / "
            "Raspberry Pi / mobile.\n\n"
            "Тобто мій досвід найсильніший з боку деплою і систем навколо quantized моделей. Глибше в quantization internals і "
            "бенчмаркинг на обмеженому залізі — це те, куди я хочу рухатись."
        ),
    },
    {
        "id": 4,
        "cat_en": "Working Without Cloud Infrastructure",
        "cat_ua": "Робота без хмарної інфраструктури",
        "q_en": "Your stack today includes Docker, Vercel, Fly.io, and Cloudflare Tunnel. This role is built around local edge systems without Kubernetes, Docker, or cloud pipelines. How would you approach building without the cloud infrastructure you have relied on so far?",
        "q_ua": "Ваш стек зараз — Docker, Vercel, Fly.io, Cloudflare Tunnel. Ця роль побудована навколо локальних edge-систем без Kubernetes, Docker і cloud pipelines. Як ви підійдете до побудови без хмарної інфраструктури, на яку ви досі спирались?",
        "a_en": (
            "I already work with this kind of setup.\n\n"
            "My current self-hosted stack includes Docker, Coolify, Cloudflare Tunnel, Tailscale, PostgreSQL, Ollama, n8n, Infisical and other "
            "internal services. The principle I use: keep boundaries explicit and services independently replaceable.\n\n"
            "For example:\n\n"
            "application / workflow layer\n→ explicit API / webhook contract\n→ validation\n→ inference or external service\n→ structured response\n→ validation + error handling\n\n"
            "That boundary stays stable whether the next hop is OpenAI, Ollama, or another local inference server.\n\n"
            "Without managed cloud, I pay more attention to areas that SaaS normally hides: service startup and restart behaviour, persistent "
            "storage, secrets management, TLS and ingress, backup and restore, health checks, logging, resource limits, deployment "
            "repeatability, failure recovery, and documenting what an operator does when something breaks.\n\n"
            "I prefer simple, reproducible systems over clever infrastructure. systemd + a documented restart procedure is often enough if the "
            "system is recoverable.\n\n"
            "For medical workloads, I treat external data flows as an architectural decision, not a default. The system makes it obvious "
            "which data stays local and which calls leave the infrastructure."
        ),
        "a_ua": (
            "Я вже працюю з таким сетапом.\n\n"
            "Мій поточний self-hosted стек: Docker, Coolify, Cloudflare Tunnel, Tailscale, PostgreSQL, Ollama, n8n, Infisical та інші внутрішні "
            "сервіси. Принцип: межі між сервісами явні, кожен сервіс можна замінити незалежно.\n\n"
            "Наприклад:\n\n"
            "application / workflow шар\n→ явний API / webhook контракт\n→ валідація\n→ інференс або зовнішній сервіс\n→ структурована відповідь\n→ валідація + обробка помилок\n\n"
            "Ця межа лишається стабільною, незалежно від того, що далі — OpenAI, Ollama, чи інший локальний inference сервер.\n\n"
            "Без managed cloud я більше уваги приділяю тому, що SaaS зазвичай ховає: поведінка сервісу при старті і рестарті, персистентне "
            "сховище, робота з секретами, TLS і ingress, бекап і відновлення, health checks, логи, resource limits, повторюваність деплою, "
            "відновлення після збоїв, документація — що оператор робить, коли щось ламається.\n\n"
            "Я віддаю перевагу простим, відтворюваним системам перед «розумною» інфраструктурою. systemd + документована процедура рестарту — "
            "часто достатньо, якщо система відновлювана.\n\n"
            "Для медичних навантажень зовнішні data flows — це архітектурне рішення, а не дефолт. З системи одразу видно, що лишається "
            "локальним, а що йде назовні."
        ),
    },
    {
        "id": 5,
        "cat_en": "Working Without Cloud Infrastructure",
        "cat_ua": "Робота без хмарної інфраструктури",
        "q_en": "Have you built anything that runs fully offline / on-device, with no external API calls at inference time?",
        "q_ua": "Чи будували ви щось, що працює повністю offline / on-device, без зовнішніх API викликів під час інференсу?",
        "a_en": (
            "I have built self-hosted inference paths where the model itself runs locally and no external LLM API is in the inference loop.\n\n"
            "I would distinguish that from a truly offline edge or embedded deployment. My current work includes Ollama-based local inference "
            "on self-hosted servers, and provider abstractions where the same application can switch between cloud providers, local Ollama, "
            "or a deterministic mock provider without rewriting the application logic.\n\n"
            "I have not yet shipped a fully offline Jetson / Raspberry Pi / mobile / embedded-device deployment.\n\n"
            "Accurate answer: yes to self-hosted local inference with no external LLM API at inference time; not yet to true edge-device "
            "deployment. PAI3's PowerNode path is exactly the kind of context where I want to close that gap."
        ),
        "a_ua": (
            "Я будував self-hosted шляхи інференції, де модель працює локально і в inference loop немає жодного зовнішнього LLM API.\n\n"
            "Це я відрізняю від справді offline edge- або embedded-деплою. Зараз у мене Ollama-інференс на self-hosted серверах і provider "
            "абстракції, де один і той самий додаток може переключатись між cloud-провайдерами, локальним Ollama або deterministic mock — "
            "без переписування application логіки.\n\n"
            "На Jetson / Raspberry Pi / mobile / embedded я ще не відправляв.\n\n"
            "Чесна відповідь: так — self-hosted локальна інференс без зовнішнього LLM API під час inference; ні — поки що не edge-device "
            "деплой. PowerNode-шлях PAI3 — це саме той контекст, де я хочу цей gap закрити."
        ),
    },
    {
        "id": 6,
        "cat_en": "Agent Orchestration",
        "cat_ua": "Оркестрація агентів",
        "q_en": "Have you used LangChain / LangGraph specifically? If not, what is your orchestration background?",
        "q_ua": "Чи використовували ви конкретно LangChain / LangGraph? Якщо ні — що у вас за background з оркестрації?",
        "a_en": (
            "I do not have production experience with LangChain or LangGraph yet.\n\n"
            "My orchestration background comes from n8n and from building my own agentic systems. One example is an AI discovery platform with "
            "specialist agents: discovery analysis, workflow analysis, security review, solution architecture, cost estimation, proposal "
            "generation, reporting. Each specialist has a defined contract, structured output, limited responsibility, and a coordinator "
            "responsible for routing and aggregation.\n\n"
            "I am also building FounderOS — an agent operating environment for long-running AI-assisted work, with mission lifecycle, "
            "persistent project context, layered memory, role boundaries, handoff rules, permissions, governance, recovery, and "
            "audit-oriented documentation.\n\n"
            "LangGraph feels conceptually familiar even without production use. My onboarding path: port one of my existing "
            "specialist-agent flows into a stateful LangGraph implementation, then compare the same workflow side-by-side with the n8n "
            "version. Learn the framework against a problem I already understand."
        ),
        "a_ua": (
            "З LangChain і LangGraph у продакшені я ще не працював.\n\n"
            "Мій оркестраційний background — це n8n і власні агентні системи. Наприклад, AI discovery платформа зі спеціалізованими "
            "агентами: discovery analysis, workflow analysis, security review, solution architecture, cost estimation, proposal generation, "
            "reporting. У кожного спеціаліста — свій контракт, структурований output, обмежена відповідальність, а координатор відповідає "
            "за routing і агрегацію.\n\n"
            "Також будую FounderOS — agent operating environment для тривалих AI-асистованих задач: mission lifecycle, persistent project "
            "context, layered memory, role boundaries, handoff rules, дозволи, governance, відновлення, audit-документація.\n\n"
            "LangGraph концептуально знайомий навіть без продакшен-використання. Мій онбординг: портувати один з моїх існуючих "
            "specialist-agent флоу у stateful LangGraph, потім порівняти той самий workflow поруч з n8n-версією. Вчити фреймворк на задачі, "
            "яку я вже розумію."
        ),
    },
    {
        "id": 7,
        "cat_en": "Agent Orchestration",
        "cat_ua": "Оркестрація агентів",
        "q_en": "How would your specialist-agent contracts and handoff patterns map onto a LangGraph-style stateful graph? What would change?",
        "q_ua": "Як ваші specialist-agent контракти і handoff-патерни мапляться на LangGraph-style stateful граф? Що зміниться?",
        "a_en": (
            "The mapping is fairly natural.\n\n"
            "Each specialist becomes a node with a narrow responsibility. The coordinator becomes a graph that controls routing and "
            "conditional transitions. Structured agent outputs become typed state fields. Decision rules become conditional edges or "
            "explicit routing functions. Human approval or escalation points map to interrupt / human-in-the-loop patterns.\n\n"
            "The biggest improvement: explicit state. In n8n, state is often implicit in the workflow execution context. In a "
            "LangGraph-style system I would define exactly which fields exist in the shared state, which node can modify them, and which "
            "transitions depend on them. Checkpointing and resumability also become more natural for long-running agent workflows.\n\n"
            "What I would not do: automatically move every automation into LangGraph. If a workflow is simple, mostly linear, and "
            "operational users need a visual editor, n8n is still the better tool. I would use LangGraph where the problem benefits "
            "from stateful branching, retries, persistent execution, long-running workflows, human approval, or multi-agent coordination."
        ),
        "a_ua": (
            "Маппинг досить природний.\n\n"
            "Кожен спеціаліст стає нодою з вузькою відповідальністю. Координатор стає графом, який контролює routing і умовні переходи. "
            "Структуровані агенні виходи стають типізованими полями стану. Правила рішень — умовними ребрами або явними routing-функціями. "
            "Точки human approval / ескалації мапляться на interrupt / human-in-the-loop патерни.\n\n"
            "Найбільший виграш: явний стан. У n8n стан часто неявний, живе у execution context. У LangGraph-style системі я б чітко "
            "визначив, які поля є в спільному state, яка нода може їх змінювати, і які переходи від них залежать. Checkpointing і "
            "resumability теж стають природнішими для довгих agent-флоу.\n\n"
            "Чого б не робив: автоматично переносити кожну автоматизацію в LangGraph. Якщо workflow простий, переважно лінійний, і "
            "операційним користувачам потрібен візуальний редактор — n8n все ще кращий інструмент. LangGraph — там, де проблема виграє "
            "від stateful branching, retries, persistent execution, довгих workflow, human approval чи multi-agent координації."
        ),
    },
    {
        "id": 8,
        "cat_en": "RAG & Reliability",
        "cat_ua": "RAG і надійність",
        "q_en": "Confidence-aware responses that refuse when context is insufficient. How is the threshold determined, and what is the false-refusal rate?",
        "q_ua": "Відповіді з урахуванням впевненості, які відмовляються, коли контексту недостатньо. Як визначається поріг, і який false-refusal rate?",
        "a_en": (
            "I have built RAG applications using PostgreSQL / pgvector, semantic and keyword retrieval, structured outputs, source "
            "citations, and confidence-aware response handling.\n\n"
            "My current implementation uses retrieval quality as a signal for whether an answer is sufficiently grounded. Important "
            "distinction: I do not present the current confidence value as a scientifically calibrated probability. The confidence "
            "mechanism is used to separate useful retrieval from empty or obviously weak retrieval, and to support refusal or fallback.\n\n"
            "If retrieval produces no relevant context, the assistant does not invent an answer. For borderline results, I prefer to "
            "expose uncertainty, log the interaction for review, or route it to a safer fallback path rather than claim high confidence.\n\n"
            "I have not built a sufficiently large held-out production evaluation set to give a defensible false-refusal rate yet.\n\n"
            "Productionization plan for PAI3:\n• build a labelled evaluation set with in-domain and out-of-domain queries\n"
            "• measure retrieval recall and answer correctness\n"
            "• sweep the retrieval / refusal threshold\n"
            "• track false answers and false refusals separately\n"
            "• pick the operating point according to the actual product risk\n\n"
            "For medical / high-risk use cases, I bias toward refusal over unsupported generation. For lower-risk internal search tools, "
            "I would allow more borderline answers but make uncertainty visible."
        ),
        "a_ua": (
            "Я будував RAG-додатки на PostgreSQL / pgvector з семантичним і keyword retrieval, structured outputs, source citations і "
            "confidence-aware обробкою відповідей.\n\n"
            "У моїй поточній реалізації якість retrieval — це сигнал, чи достатньо контексту для відповіді. Важлива різниця: я не подаю "
            "поточне значення confidence як науково відкалібровану ймовірність. Механізм потрібен, щоб відрізнити корисний retrieval від "
            "порожнього чи явно слабкого — і підтримати refuse / fallback.\n\n"
            "Якщо retrieval не дає релевантного контексту — асистент не вигадує відповідь. Для граничних випадків я вважаю за краще "
            "видимо показати невпевненість, логувати взаємодію на рев'ю, або скеровувати у безпечніший fallback, ніж заявляти високу "
            "confidence.\n\n"
            "Достатньо великого held-out production eval-сету, щоб дати обґрунтований false-refusal rate, у мене поки немає.\n\n"
            "План production-ization для PAI3:\n• зібрати labelled eval-сет з in-domain і out-of-domain запитами\n"
            "• виміряти retrieval recall і correctness відповіді\n"
            "• прогнати sweep по retrieval / refusal threshold\n"
            "• окремо трекати false answers і false refusals\n"
            "• обрати operating point під реальний ризик продукту\n\n"
            "Для медичних / high-risk кейсів я схиляюсь до refuse замість непідкріпленої генерації. Для нижчого ризику, "
            "внутрішніх пошукових тулзів — дозволю більше граничних відповідей, але з видимою невпевненістю."
        ),
    },
    {
        "id": 9,
        "cat_en": "RAG & Reliability",
        "cat_ua": "RAG і надійність",
        "q_en": "Local data flow and audit trail for a medical / intranet deployment. How would you design it?",
        "q_ua": "Локальний data flow і audit trail для медичного / інтранет-деплою. Як би ви його спроєктували?",
        "a_en": (
            "First principle: the patient data never leaves the intranet boundary. Every component that touches PHI runs on a PowerNode "
            "or on a service inside the same network segment. Any external call must be explicit, allowlisted, and logged.\n\n"
            "Layered design:\n\n"
            "1. Ingress. Cloudflare Tunnel (or a hospital-internal reverse proxy) terminates TLS, enforces authn / authz, and routes only "
            "to services inside the network. No service is directly reachable from the internet.\n\n"
            "2. Application layer. Stateless API that handles auth, validates input, calls the inference service, validates the output, "
            "and writes an audit-log entry. Holds no PHI between requests.\n\n"
            "3. Inference layer. Ollama or another local model server running the fine-tuned / base model. No network egress — pulls new "
            "model artifacts only through a controlled, signed, and human-reviewed process.\n\n"
            "4. Data layer. PostgreSQL with pgvector for embeddings and metadata. Backups encrypted at rest, rotated, restored on a "
            "schedule, and the restore procedure itself is tested.\n\n"
            "5. Audit log. Append-only, signed, replicated. Every inference call records: timestamp, user, request ID, model version, "
            "retrieved chunk IDs, refusal / response, latency. Tamper-evident, exportable for regulator inspection.\n\n"
            "6. Secrets. Infisical or HashiCorp Vault — never in container images, never in env files committed to git, rotated on a "
            "schedule.\n\n"
            "7. Observability. Structured JSON logs to a local Loki or journald. Metrics in Prometheus. p99 latency, tokens/sec, refusal "
            "rate, retrieval score distribution — the metrics an on-call clinician actually needs.\n\n"
            "Failure handling: every external call is idempotent so retries are safe. Rollback = swap model version pointer. Blue/green "
            "for model rollouts. Soak tests before any production change.\n\n"
            "Governance: model versions are documented in a registry; every production change has an ADR with rollback criteria; "
            "human-in-the-loop is required for any irreversible action. PAI3 PowerNode model updates use the same audit-trail discipline "
            "as a clinical software release."
        ),
        "a_ua": (
            "Перший принцип: дані пацієнтів ніколи не виходять за межі інтранету. Кожен компонент, що торкається PHI, працює на "
            "PowerNode або на сервісі всередині того ж мережевого сегмента. Будь-який зовнішній виклик — явний, в allowlist, логований.\n\n"
            "Пошарова архітектура:\n\n"
            "1. Ingress. Cloudflare Tunnel (або внутрішньо-лікарняний reverse proxy) — термінує TLS, перевіряє authn / authz, і роутить "
            "тільки до сервісів всередині мережі. Жоден сервіс не доступний з інтернету напряму.\n\n"
            "2. Application шар. Stateless API, який перевіряє auth, валідує input, викликає inference сервіс, валідує output, пише "
            "audit-запис. Не зберігає PHI між запитами.\n\n"
            "3. Inference шар. Ollama або інший локальний model server з fine-tuned / базовою моделлю. Без мережевого egress — нові "
            "артефакти моделі підтягуються тільки контрольовано, з підписом і human review.\n\n"
            "4. Data шар. PostgreSQL з pgvector для embeddings і метаданих. Бекапи зашифровані at rest, ротуються, відновлення на "
            "розкладі, процедура відновлення сама по собі тестується.\n\n"
            "5. Audit log. Append-only, підписаний, реплікований. Кожен inference-виклик фіксує: timestamp, user, request ID, версію "
            "моделі, ID retrieved чанків, refusal / response, latency. Tamper-evident, експортується для регулятора.\n\n"
            "6. Секрети. Infisical або HashiCorp Vault — не в образах контейнерів, не в env-файлах у git, ротуються за розкладом.\n\n"
            "7. Observability. Структуровані JSON логи в локальний Loki або journald. Метрики в Prometheus. p99 latency, tokens/sec, "
            "refusal rate, розподіл retrieval score — ті метрики, що реально потрібні черговому лікарю.\n\n"
            "Обробка збоїв: кожен зовнішній виклик idempotent — retries безпечні. Rollback = змінити pointer на версію моделі. Blue/green "
            "для model rollouts. Soak tests перед кожною production-зміною.\n\n"
            "Governance: версії моделей — у реєстрі; кожна production-зміна має ADR з rollback-критеріями; human-in-the-loop обов'язковий "
            "для будь-якої незворотної дії. Оновлення моделей на PAI3 PowerNode — з тією ж audit-trail дисципліною, що й реліз клінічного ПЗ."
        ),
    },
    {
        "id": 10,
        "cat_en": "RAG & Reliability",
        "cat_ua": "RAG і надійність",
        "q_en": "How would you validate that a local model's output is safe and correct enough for a clinical / medical workflow?",
        "q_ua": "Як би ви перевіряли, що вихід локальної моделі досить безпечний і коректний для клінічного / медичного workflow?",
        "a_en": (
            "Validation is layered, not a single test.\n\n"
            "Layer 1 — offline evaluation. Build a labelled eval set that reflects real clinical use: in-domain (symptom summaries, "
            "drug interaction queries, discharge-note drafts) and adversarial (off-topic, ambiguous, deliberately misleading). Run the "
            "model on this set, score answers against ground truth, measure precision, recall, and refusal rate.\n\n"
            "Layer 2 — guardrails. Pre-LLM filters reject prompt-injection and off-scope queries. Post-LLM validators check: "
            "no fabricated drug doses or contraindications, no invented patient IDs, citations present where required, output matches "
            "the declared schema. Hard refusals for anything outside the approved scope.\n\n"
            "Layer 3 — shadow mode. The new model runs alongside production for 1-2 weeks, sees real queries, but its outputs are "
            "logged and reviewed, not shown to clinicians. Compare against the current model on the same queries.\n\n"
            "Layer 4 — human-in-the-loop. For a clinical assistant, the model's output is always a draft until a clinician signs off. "
            "Never a fully autonomous decision.\n\n"
            "Layer 5 — continuous monitoring. In production: track refusal rate, retrieval confidence distribution, schema validation "
            "failures, and (where allowed) clinician override rate. Drift triggers a model rollback.\n\n"
            "For regulated medical AI, this process is not optional — it is the documented evidence that the system is fit for "
            "purpose, required by HIPAA and equivalent regulations."
        ),
        "a_ua": (
            "Валідація — пошарова, не один тест.\n\n"
            "Шар 1 — offline evaluation. Зібрати labelled eval-сет, який відображає реальне клінічне використання: in-domain (підсумки "
            "симптомів, запити на взаємодію ліків, чернетки виписок) і adversarial (off-topic, неоднозначні, навмисно маніпулятивні). "
            "Прогнати модель на цьому сеті, оцінити відповіді проти ground truth, виміряти precision, recall, refusal rate.\n\n"
            "Шар 2 — guardrails. Pre-LLM фільтри відсіюють prompt-injection і запити поза скоупом. Post-LLM валідатори перевіряють: "
            "немає вигаданих доз ліків чи протипоказань, немає вигаданих patient ID, citations присутні де треба, вихід відповідає "
            "заявленій схемі. Hard refusals на все, що поза затвердженим скоупом.\n\n"
            "Шар 3 — shadow mode. Нова модель працює поруч з продакшеном 1-2 тижні, бачить реальні запити, але її виходи логуються і "
            "рев'юються — не показуються клініцистам. Порівняння з поточною моделлю на тих самих запитах.\n\n"
            "Шар 4 — human-in-the-loop. Для клінічного асистента вихід моделі — завжди чернетка, доки клініцист не підпише. Ніколи не "
            "повністю автономне рішення.\n\n"
            "Шар 5 — безперервний моніторинг. У продакшені: трекати refusal rate, розподіл retrieval confidence, schema validation "
            "failures, і (де дозволено) clinician override rate. Drift тригерить rollback моделі.\n\n"
            "Для регульованого medical AI цей процес не опціональний — це документований доказ fitness for purpose, вимога HIPAA і "
            "еквівалентних регуляцій."
        ),
    },
    {
        "id": 11,
        "cat_en": "Systems & Reliability",
        "cat_ua": "Системи і надійність",
        "q_en": "How do you make a locally-deployed AI system observable and recoverable in production?",
        "q_ua": "Як ви робите локально-розгорнуту AI систему observable і таку, що відновлюється у продакшені?",
        "a_en": (
            "Observability. Three pillars, plus an LLM-specific fourth.\n\n"
            "Logs — structured JSON to a local aggregator. Each inference call records: request ID, user, model version, prompt hash "
            "(not full PHI), retrieved chunk IDs, response hash, refusal flag, latency. Queryable by request ID and by user.\n\n"
            "Metrics — Prometheus, scraped from each PowerNode. Tokens/sec, p50 / p99 latency, request rate, error rate, GPU utilisation, "
            "memory pressure, queue depth. The metrics an on-call engineer needs at 3am.\n\n"
            "Traces — OpenTelemetry across the request path: ingress → API → retrieval → inference → response. Lets you see which hop "
            "is slow when something regresses.\n\n"
            "LLM-specific — prompt/response quality metrics: retrieval confidence distribution, schema validation failure rate, refusal "
            "rate, clinician override rate (where applicable). Drift in any of these is the canary.\n\n"
            "Recoverability.\n\n"
            "Backups — encrypted, tested restore procedure, off-node. Postgres WAL archived continuously.\n\n"
            "Rollback — every model version is a tagged artifact. Production points at a version pointer. Rollback = one config change "
            "+ restart, takes 30 seconds.\n\n"
            "Blue/green model rollouts — new model version runs in parallel, traffic flipped atomically after validation.\n\n"
            "Idempotency — every external call has an idempotency key. Retries are safe.\n\n"
            "Health checks — load balancer pulls a `/health` endpoint that checks the inference server, the vector DB, and the secrets "
            "vault. A failing node is removed from rotation automatically.\n\n"
            "Soak tests — before any production change, run a 4-hour load test against a staging PowerNode. Catches memory leaks and "
            "slow drift that 5-minute smoke tests miss.\n\n"
            "Documentation — every recoverable failure has a runbook entry. The on-call clinician or engineer can resolve the "
            "top-10 incidents without paging anyone."
        ),
        "a_ua": (
            "Observability. Три класичні стовпи плюс один LLM-специфічний.\n\n"
            "Логи — структурований JSON у локальний агрегатор. Кожен inference-виклик фіксує: request ID, user, версію моделі, prompt hash "
            "(не повний PHI), ID retrieved чанків, response hash, refusal flag, latency. Запитується за request ID і user.\n\n"
            "Метрики — Prometheus, з кожного PowerNode. Tokens/sec, p50 / p99 latency, request rate, error rate, GPU utilisation, тиск "
            "на пам'ять, queue depth. Ті метрики, що потрібні черговому інженеру о 3-й ночі.\n\n"
            "Трейси — OpenTelemetry по всьому шляху запиту: ingress → API → retrieval → inference → response. Видно, який hop тупить, "
            "коли щось регресує.\n\n"
            "LLM-специфічне — метрики якості prompt/response: розподіл retrieval confidence, schema validation failure rate, refusal "
            "rate, clinician override rate (де застосовно). Drift по будь-якій з них — це канарейка.\n\n"
            "Відновлюваність.\n\n"
            "Бекапи — зашифровані, перевірена процедура відновлення, поза нодою. Postgres WAL архівується неперервно.\n\n"
            "Rollback — кожна версія моделі — це tagged artifact. Продакшен вказує на version pointer. Rollback = одна зміна конфігу + "
            "рестарт, 30 секунд.\n\n"
            "Blue/green model rollouts — нова версія моделі працює паралельно, трафік переключається атомарно після валідації.\n\n"
            "Idempotency — кожен зовнішній виклик має idempotency key. Retries безпечні.\n\n"
            "Health checks — load balancer смикає `/health` ендпоінт, який перевіряє inference server, vector DB і secrets vault. "
            "Нода, що відпала, автоматично прибирається з ротації.\n\n"
            "Soak tests — перед кожною production-зміною 4-годинний load-тест на staging PowerNode. Ловить memory leaks і повільний "
            "drift, які 5-хвилинні smoke-тести пропускають.\n\n"
            "Документація — на кожен відновлюваний збій є runbook-запис. Черговий клініцист або інженер вирішує топ-10 інцидентів без "
            "залучення когось."
        ),
    },
    {
        "id": 12,
        "cat_en": "Background & Role Fit",
        "cat_ua": "Background і fit під роль",
        "q_en": "What fraction of your AI systems work has been solo / greenfield, vs. inside an existing team?",
        "q_ua": "Яка частка вашої роботи з AI-системами — solo / greenfield, а яка — всередині існуючої команди?",
        "a_en": (
            "Both, deliberately.\n\n"
            "Greenfield — a public n8n-based AI portfolio assistant, a RAG customer-support application, an AI discovery platform with "
            "specialist agents, and FounderOS — an agent operating environment for long-running AI-assisted work with persistent "
            "context, governance, memory, recovery, and auditability. In those projects I owned architecture, implementation, integration, "
            "deployment, testing, and documentation.\n\n"
            "Inside an existing team — my current work runs on self-hosted AI infrastructure at my company, alongside the leadership "
            "and AI automation specialists. My responsibilities there include architecture audits, target-state design, ADRs, internal "
            "infrastructure, secrets and access workflows, deployment practices, agent configuration, technical documentation, recovery "
            "planning, and task decomposition for a small AI automation team.\n\n"
            "I also build reusable AI-assisted QA and internal engineering workflows — the goal is not to replace people but to reduce "
            "repetitive work and make execution more consistent.\n\n"
            "So: comfortable with both — starting from a blank page and owning the whole system, and entering an existing environment "
            "where changes must respect current constraints, people, data, and operational processes. My current trajectory is from AI "
            "Automation Engineer toward Solution Architect / AI Systems Engineer, so the team-architecture side is something I am "
            "deliberately deepening."
        ),
        "a_ua": (
            "І те, і те — навмисно.\n\n"
            "Greenfield — публічний n8n-based AI portfolio assistant, RAG customer-support додаток, AI discovery платформа зі "
            "спеціалізованими агентами, FounderOS — agent operating environment для тривалих AI-асистованих задач з persistent "
            "context, governance, memory, recovery і auditability. У цих проектах я відповідав за архітектуру, реалізацію, інтеграції, "
            "деплой, тестування і документацію.\n\n"
            "У складі команди — моя поточна робота йде на self-hosted AI інфраструктурі в моїй компанії, разом з керівництвом і AI "
            "automation спеціалістами. Мої обов'язки: architecture audits, target-state design, ADRs, внутрішня інфраструктура, "
            "секрети і доступи, deployment practices, конфігурація агентів, технічна документація, recovery planning і декомпозиція "
            "задач для невеликої AI automation команди.\n\n"
            "Також будую reusable AI-асистовані QA і внутрішні engineering-флоу — мета не замінити людей, а прибрати повторювану роботу "
            "і зробити виконання більш консистентним.\n\n"
            "Тобто: комфортно і з чистого аркуша, і всередині існуючого середовища, де зміни мають поважати поточні обмеження, людей, "
            "дані й операційні процеси. Мій поточний трек — від AI Automation Engineer до Solution Architect / AI Systems Engineer, "
            "тому командно-архітектурну сторону я свідомо поглиблюю."
        ),
    },
    {
        "id": 13,
        "cat_en": "Background & Role Fit",
        "cat_ua": "Background і fit під роль",
        "q_en": "What draws you to PAI3's shift away from traditional backend / cloud pipelines toward local, decentralized AI?",
        "q_ua": "Що вас приваблює у PAI3 — у зсуві від традиційних backend / cloud pipelines до локального, децентралізованого AI?",
        "a_en": (
            "The hard part of AI is no longer 'build an API and deploy it'. It is making AI behaviour fit into a reliable production "
            "system where failure modes are new, debugging is non-deterministic, and every architectural choice is a privacy or cost "
            "trade-off.\n\n"
            "What interests me most is the combination:\n• local or self-hosted inference\n• agentic systems\n• retrieval and context\n"
            "• evaluation\n• security boundaries\n• human-in-the-loop control\n• recovery\n• observability\n• explicit operational governance\n\n"
            "PAI3 sits exactly at that intersection. PowerNodes, no Kubernetes, no Docker dependency, model rollouts as a first-class "
            "concept — these are the kinds of constraints that make the engineering work interesting.\n\n"
            "I am not moving away from engineering discipline. I am applying the same discipline to AI systems. I still care about "
            "explicit contracts, structured inputs and outputs, idempotency, failure modes, testing, deployment repeatability, "
            "observability, documentation, and recovery. The difference is that AI adds another layer of uncertainty, so those "
            "practices become more important, not less.\n\n"
            "My longer-term direction: AI Automation Engineer → AI Systems Engineer / Solution Architect → building and owning larger "
            "AI products and platforms. The medical / intranet angle matters to me personally — I want the systems I build to be "
            "deployable where they protect people, not just where they make a margin.\n\n"
            "I already bring the surrounding systems experience. The areas I want to deepen are PyTorch, LoRA / QLoRA, quantization "
            "internals, hardware-aware inference optimization, and true edge deployment — exactly the PAI3 surface area."
        ),
        "a_ua": (
            "Складна частина AI вже не «побудувати API і задеплоїти». Це зробити поведінку AI частиною надійної production-системи, де "
            "режими відмов — нові, дебаг — недетерміністичний, і кожне архітектурне рішення — це trade-off приватності чи вартості.\n\n"
            "Що мене найбільше цікавить — це комбінація:\n• локальна або self-hosted інференс\n• агентні системи\n• retrieval і контекст\n"
            "• evaluation\n• межі безпеки\n• human-in-the-loop контроль\n• recovery\n• observability\n• явна операційна governance\n\n"
            "PAI3 сидить рівно на цьому перетині. PowerNodes, без Kubernetes, без залежності від Docker, model rollouts як "
            "first-class концепція — це ті обмеження, які роблять інженерну роботу цікавою.\n\n"
            "Я не йду від інженерної дисципліни. Я застосовую ту ж дисципліну до AI-систем. Мені й далі важливі явні контракти, "
            "структуровані inputs/outputs, idempotency, failure modes, тестування, повторюваність деплою, observability, документація, "
            "recovery. Різниця в тому, що AI додає ще один шар невизначеності — і ці практики стають важливішими, а не менш.\n\n"
            "Мій довгостроковий напрямок: AI Automation Engineer → AI Systems Engineer / Solution Architect → будувати і володіти "
            "більшими AI продуктами і платформами. Медичний / інтранет кут для мене особисто — я хочу, щоб системи, які я будую, "
            "могли розгортатись там, де вони захищають людей, а не просто там, де вони дають маржу.\n\n"
            "Оточуючий systems experience у мене вже є. Сфери, які хочу поглибити — PyTorch, LoRA / QLoRA, quantization internals, "
            "hardware-aware inference optimization, справжній edge deployment — це саме surface area PAI3."
        ),
    },
]


# ============================================================================
# HELPERS
# ============================================================================

def js_literal(s):
    """Python str -> JS string literal. Must escape </ to avoid HTML break."""
    s = s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("</", "<\\/")
    return f"'{s}'"


def render_qa_html(questions, lang):
    """Build the HTML for all Q&A blocks. Auto-wraps glossary terms."""
    # Sort glossary terms longest-first to prefer multi-word matches.
    sorted_terms = sorted(GLOSSARY.keys(), key=lambda k: -len(GLOSSARY[k]["term"]))

    # Build a regex pattern that catches glossary terms case-insensitively.
    # We match the exact surface form from GLOSSARY (case-insensitive) to a unique id.
    import re
    pattern_parts = []
    for gid in sorted_terms:
        term = GLOSSARY[gid]["term"]
        # Escape regex specials in term text.
        pattern_parts.append(re.escape(term))
    # word boundary at start to avoid partial matches inside other words.
    combined = re.compile(r"\b(" + "|".join(pattern_parts) + r")\b", re.IGNORECASE)

    def replace_term(match):
        text = match.group(0)
        # Find which glossary term this matches (case-insensitive dict lookup).
        for gid in sorted_terms:
            if text.lower() == GLOSSARY[gid]["term"].lower():
                return (
                    f'<span class="term" data-term="{gid}">{text}</span>'
                )
        return text

    qa_blocks = []
    for q in questions:
        cat = q["cat_en"] if lang == "en" else q["cat_ua"]
        question = q["q_en"] if lang == "en" else q["q_ua"]
        answer = q["a_en"] if lang == "en" else q["a_ua"]
        answer_html = combined.sub(replace_term, ihtml.escape(answer))
        # Preserve paragraph breaks: split on \n\n into <p>.
        paragraphs = []
        for chunk in answer_html.split("\n\n"):
            chunk = chunk.strip()
            if not chunk:
                continue
            # If the chunk itself starts with a bullet/number/arrow, treat as a list.
            lines = chunk.split("\n")
            if all(l.lstrip().startswith(("•", "→", "-", "*")) for l in lines if l.strip()):
                items = "".join(f"<li>{l.lstrip().lstrip('•→-* ').strip()}</li>" for l in lines if l.strip())
                paragraphs.append(f"<ul class='qa-list'>{items}</ul>")
            else:
                paragraphs.append(f"<p>{chunk.replace(chr(10), '<br>')}</p>")
        answer_block = "\n".join(paragraphs)

        qa_blocks.append(f"""
        <article class="qa-card" id="q-{q['id']}">
          <header class="qa-head">
            <span class="qa-num">Q{q['id']:02d}</span>
            <span class="qa-cat">{ihtml.escape(cat)}</span>
          </header>
          <h3 class="qa-q">{ihtml.escape(question)}</h3>
          <div class="qa-a">{answer_block}</div>
        </article>""")
    return "\n".join(qa_blocks)


def render_glossary_data(lang="en"):
    """Build a JS object literal for the glossary, for hover lookup.

    lang='en' -> emits EN short/long; lang='uk' -> emits UA short/long.
    The 'id' field is always the canonical glossary id (used for data-term).
    The 'term' field in JS is the DISPLAY label — EN for EN page, UA for UA page
    (so the tooltip header reads in the user's language even though the
    matched prose surface form is EN).
    """
    items = []
    for gid, g in GLOSSARY.items():
        if lang == "uk":
            ua = UA_GLOSSARY.get(gid, {})
            short = ua.get("short", g["short"])
            long_ = ua.get("long", g["long"])
            display_term = ua.get("term", g["term"])
        else:
            short = g["short"]
            long_ = g["long"]
            display_term = g["term"]
        items.append(
            f"  {js_literal(gid)}: {{id:{js_literal(gid)},term:{js_literal(display_term)},"
            f"short:{js_literal(short)},long:{js_literal(long_)}}}"
        )
    return "const GLOSSARY = {\n" + ",\n".join(items) + "\n};"


def render_term_index_data():
    """A flat term -> id map for fast lookup during render."""
    items = [f"  {js_literal(g['term'])}: {js_literal(gid)}" for gid, g in GLOSSARY.items()]
    return "const TERM_INDEX = {\n" + ",\n".join(items) + "\n};"


def page_html(lang, qa_html, lang_label, other_lang_url, other_lang_label):
    title = (
        "PAI3 Network — AI Systems Engineer — Interview Cheatsheet"
        if lang == "en"
        else "PAI3 Network — AI Systems Engineer — Шпаргалка до співбесіди"
    )
    subtitle = (
        "Pre-interview Q&A · 13 questions · hover any term for a tooltip"
        if lang == "en"
        else "Питання і відповіді до співбесіди · 13 питань · наведіть на термін для підказки"
    )
    author_line = "Taras Polishchuk · 2026-09-18 · 16:00 Kyiv technical interview"
    other_link_label = "Other language" if lang == "en" else "Інша мова"

    js_glossary = render_glossary_data(lang=lang)
    js_index = render_term_index_data()

    # initial tooltip + search index built from GLOSSARY at runtime.
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{ihtml.escape(title)}</title>
<meta name="description" content="{ihtml.escape(subtitle)}">
<style>
  :root {{
    --bg: #0e0e10;
    --bg-elev: #16161a;
    --bg-soft: #1c1c22;
    --border: #2a2a32;
    --border-strong: #3a3a46;
    --fg: #e6e6ea;
    --fg-dim: #a0a0aa;
    --fg-mute: #6e6e78;
    --accent: #d97757;          /* Claude Code orange */
    --accent-soft: rgba(217,119,87,0.12);
    --link: #7aa2f7;
    --kbd-bg: #23232b;
    --serif: ui-serif, Charter, "Iowan Old Style", Georgia, serif;
    --mono: ui-monospace, "JetBrains Mono", "SF Mono", Menlo, Consolas, monospace;
    --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, system-ui, sans-serif;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ background: var(--bg); color: var(--fg); margin: 0; }}
  body {{
    font-family: var(--mono);
    font-size: 14.5px;
    line-height: 1.65;
    -webkit-font-smoothing: antialiased;
  }}
  a {{ color: var(--link); text-decoration: none; }}
  a:hover {{ text-decoration: underline; }}
  .wrap {{ max-width: 880px; margin: 0 auto; padding: 48px 24px 96px; }}

  /* Header / hero */
  header.hero {{
    border-bottom: 1px solid var(--border);
    padding-bottom: 28px;
    margin-bottom: 36px;
  }}
  .prompt-line {{
    color: var(--accent);
    font-family: var(--mono);
    font-size: 13px;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .prompt-line::before {{ content: "❯"; font-weight: 700; }}
  h1 {{
    font-family: var(--mono);
    font-weight: 600;
    font-size: 24px;
    line-height: 1.25;
    margin: 0 0 8px;
    letter-spacing: -0.01em;
  }}
  .sub {{ color: var(--fg-dim); font-size: 13.5px; margin-bottom: 16px; }}
  .meta {{
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    font-size: 12px;
    color: var(--fg-mute);
    border-top: 1px dashed var(--border);
    padding-top: 14px;
  }}
  .meta b {{ color: var(--fg-dim); font-weight: 500; }}
  .lang-switch {{
    margin-left: auto;
    padding: 4px 10px;
    border: 1px solid var(--border-strong);
    border-radius: 4px;
    font-size: 12px;
    color: var(--fg-dim);
  }}
  .lang-switch:hover {{ background: var(--bg-soft); text-decoration: none; }}

  /* Index of questions */
  .index {{
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px 16px;
    margin-bottom: 36px;
    background: var(--bg-elev);
    font-size: 12.5px;
  }}
  .index-title {{
    color: var(--fg-mute);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 10.5px;
    margin-bottom: 10px;
  }}
  .index ul {{ list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: 1fr 1fr; gap: 4px 16px; }}
  .index a {{ color: var(--fg-dim); }}
  .index a:hover {{ color: var(--accent); }}
  .index .num {{ color: var(--fg-mute); margin-right: 6px; }}

  /* Q&A cards */
  .qa-card {{
    border: 1px solid var(--border);
    border-left: 2px solid var(--accent);
    border-radius: 4px;
    padding: 18px 22px;
    margin-bottom: 18px;
    background: var(--bg-elev);
    transition: border-color 120ms;
  }}
  .qa-card:hover {{ border-color: var(--border-strong); }}
  .qa-head {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }}
  .qa-num {{
    color: var(--accent);
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.06em;
  }}
  .qa-cat {{
    color: var(--fg-mute);
    font-size: 11px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }}
  .qa-q {{
    font-family: var(--mono);
    font-weight: 500;
    font-size: 15.5px;
    line-height: 1.4;
    color: var(--fg);
    margin: 4px 0 12px;
  }}
  .qa-a {{ color: var(--fg-dim); font-size: 14px; line-height: 1.7; }}
  .qa-a p {{ margin: 0 0 12px; }}
  .qa-a p:last-child {{ margin-bottom: 0; }}
  .qa-list {{ margin: 6px 0 12px; padding-left: 18px; }}
  .qa-list li {{ margin-bottom: 4px; color: var(--fg-dim); }}
  .qa-list li::marker {{ color: var(--accent); }}

  /* Term tooltips */
  .term {{
    border-bottom: 1px dotted var(--accent);
    cursor: help;
    color: var(--fg);
    transition: background 80ms;
  }}
  .term:hover {{
    background: var(--accent-soft);
  }}
  #tooltip {{
    position: fixed;
    z-index: 1000;
    max-width: 380px;
    background: #111114;
    border: 1px solid var(--accent);
    border-radius: 4px;
    padding: 10px 12px;
    font-size: 12.5px;
    line-height: 1.5;
    color: var(--fg);
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    pointer-events: none;
    opacity: 0;
    transform: translateY(4px);
    transition: opacity 90ms, transform 90ms;
  }}
  #tooltip.show {{ opacity: 1; transform: translateY(0); }}
  #tooltip .tt-term {{
    color: var(--accent);
    font-weight: 600;
    font-size: 13px;
    margin-bottom: 4px;
    display: block;
  }}
  #tooltip .tt-short {{ color: var(--fg-dim); }}
  #tooltip .tt-more {{
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px solid var(--border);
    color: var(--fg-mute);
    font-size: 11.5px;
    line-height: 1.5;
  }}

  /* Modal for full term detail */
  #modal {{
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.7);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 2000;
    padding: 24px;
    backdrop-filter: blur(6px);
  }}
  #modal.show {{ display: flex; }}
  .modal-card {{
    background: var(--bg-elev);
    border: 1px solid var(--border-strong);
    border-radius: 6px;
    max-width: 640px;
    width: 100%;
    max-height: 80vh;
    overflow-y: auto;
    padding: 28px;
  }}
  .modal-card h3 {{
    margin: 0 0 8px;
    color: var(--accent);
    font-size: 18px;
    font-family: var(--mono);
    font-weight: 600;
  }}
  .modal-card .m-short {{
    font-size: 14px;
    color: var(--fg);
    margin-bottom: 14px;
    line-height: 1.6;
  }}
  .modal-card .m-long {{
    font-size: 13px;
    color: var(--fg-dim);
    line-height: 1.65;
    border-top: 1px solid var(--border);
    padding-top: 14px;
  }}
  .modal-close {{
    margin-top: 18px;
    background: transparent;
    border: 1px solid var(--border-strong);
    color: var(--fg-dim);
    padding: 6px 14px;
    border-radius: 4px;
    cursor: pointer;
    font-family: var(--mono);
    font-size: 12px;
  }}
  .modal-close:hover {{ background: var(--bg-soft); color: var(--fg); }}

  /* Glossary sidebar */
  .glossary-toggle {{
    position: fixed;
    bottom: 18px;
    right: 18px;
    background: var(--bg-elev);
    border: 1px solid var(--accent);
    color: var(--accent);
    padding: 8px 14px;
    border-radius: 20px;
    font-family: var(--mono);
    font-size: 12px;
    cursor: pointer;
    z-index: 500;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  }}
  .glossary-toggle:hover {{ background: var(--accent); color: var(--bg); }}
  #glossary-panel {{
    position: fixed;
    top: 0; right: 0;
    width: 360px;
    max-width: 100vw;
    height: 100vh;
    background: var(--bg);
    border-left: 1px solid var(--border);
    transform: translateX(100%);
    transition: transform 200ms ease-out;
    z-index: 1500;
    overflow-y: auto;
    padding: 20px;
  }}
  #glossary-panel.open {{ transform: translateX(0); }}
  #glossary-panel h3 {{
    font-family: var(--mono);
    font-size: 14px;
    color: var(--accent);
    margin: 0 0 4px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}
  #glossary-panel .gp-close {{
    float: right;
    background: transparent;
    border: none;
    color: var(--fg-mute);
    font-size: 18px;
    cursor: pointer;
    line-height: 1;
  }}
  #glossary-panel .gp-search {{
    width: 100%;
    margin: 12px 0 16px;
    padding: 7px 10px;
    background: var(--bg-soft);
    border: 1px solid var(--border);
    border-radius: 4px;
    color: var(--fg);
    font-family: var(--mono);
    font-size: 12.5px;
  }}
  #glossary-panel .gp-search:focus {{ outline: none; border-color: var(--accent); }}
  .gp-item {{
    padding: 8px 10px;
    border-radius: 3px;
    cursor: pointer;
    margin-bottom: 2px;
  }}
  .gp-item:hover {{ background: var(--bg-soft); }}
  .gp-term {{ color: var(--accent); font-weight: 500; font-size: 12.5px; }}
  .gp-short {{ color: var(--fg-dim); font-size: 11.5px; line-height: 1.45; margin-top: 2px; }}
  .gp-empty {{ color: var(--fg-mute); font-size: 12px; padding: 10px; }}

  /* Footer */
  footer.foot {{
    margin-top: 48px;
    padding-top: 24px;
    border-top: 1px solid var(--border);
    color: var(--fg-mute);
    font-size: 11.5px;
    line-height: 1.6;
  }}

  /* Mobile */
  @media (max-width: 720px) {{
    .wrap {{ padding: 28px 16px 80px; }}
    h1 {{ font-size: 19px; }}
    .index ul {{ grid-template-columns: 1fr; }}
    .qa-card {{ padding: 14px 16px; }}
    #glossary-panel {{ width: 100vw; }}
  }}

  /* Print */
  @media print {{
    :root {{ --bg:#fff; --bg-elev:#fff; --bg-soft:#fafafa; --fg:#000; --fg-dim:#222;
            --fg-mute:#555; --border:#ccc; --border-strong:#888; --accent:#933; }}
    body {{ background:#fff; color:#000; }}
    .glossary-toggle, #glossary-panel, #tooltip {{ display:none !important; }}
    .qa-card {{ break-inside: avoid; border-left-color:#933; }}
    .term {{ border-bottom: 1px dotted #933; }}
  }}
</style>
</head>
<body>
<div class="wrap">

  <header class="hero">
    <div class="prompt-line">PAI3-NETWORK · INTERVIEW-CHEATSHEET</div>
    <h1>{ihtml.escape(title)}</h1>
    <div class="sub">{ihtml.escape(subtitle)}</div>
    <div class="meta">
      <span><b>Candidate:</b> Taras Polishchuk</span>
      <span><b>Role:</b> AI Systems Engineer</span>
      <span><b>Vacancy:</b> DOU #364636</span>
      <span><b>Generated:</b> 2026-09-18</span>
      <a class="lang-switch" href="{ihtml.escape(other_lang_url)}">← {ihtml.escape(other_lang_label)}</a>
    </div>
  </header>

  <nav class="index">
    <div class="index-title">// Questions in this pack</div>
    <ul>
      {''.join(f'<li><a href="#q-{q["id"]}"><span class="num">Q{q["id"]:02d}</span>{ihtml.escape((q["q_en"] if lang=="en" else q["q_ua"])[:80] + ("…" if len(q["q_en"] if lang=="en" else q["q_ua"]) > 80 else ""))}</a></li>' for q in QUESTIONS)}
    </ul>
  </nav>

  <main>
    {qa_html}
  </main>

  <footer class="foot">
    <div>{ihtml.escape(author_line)}</div>
    <div style="margin-top:8px">
      {ihtml.escape('Hover any' if lang == 'en' else 'Наведіть на будь-який')} <span class="term" data-term="ollama">{ihtml.escape('underlined term' if lang == 'en' else 'підкреслений термін')}</span> {ihtml.escape('for a one-line tooltip. Click it for the full definition.' if lang == 'en' else 'для короткого tooltip. Клік — повне пояснення.')}
      {ihtml.escape('Press' if lang == 'en' else 'Натисніть')} <kbd>/</kbd> {ihtml.escape('to jump to a term via the glossary panel.' if lang == 'en' else 'щоб перейти до терміна через панель глосарія.')}
    </div>
  </footer>

</div>

<div id="tooltip" role="tooltip" aria-hidden="true">
  <span class="tt-term"></span>
  <div class="tt-short"></div>
  <div class="tt-more" style="display:none"></div>
</div>

<div id="modal" role="dialog" aria-modal="true" aria-hidden="true">
  <div class="modal-card">
    <h3 id="modal-term"></h3>
    <div class="m-short" id="modal-short"></div>
    <div class="m-long" id="modal-long"></div>
    <button class="modal-close" id="modal-close">Close (Esc)</button>
  </div>
</div>

<button class="glossary-toggle" id="gp-toggle">📖 {ihtml.escape('Glossary' if lang == 'en' else 'Глосарій')}</button>
<div id="glossary-panel">
  <button class="gp-close" id="gp-close" aria-label="Close">×</button>
  <h3>{ihtml.escape('Glossary' if lang == 'en' else 'Глосарій')} · {len(GLOSSARY)} {ihtml.escape('terms' if lang == 'en' else 'термінів')}</h3>
  <input type="text" class="gp-search" id="gp-search" placeholder="{ihtml.escape('Search terms…' if lang == 'en' else 'Пошук термінів…')}" autocomplete="off">
  <div id="gp-list"></div>
</div>

<script>
{js_glossary}
{js_index}

const tooltip = document.getElementById('tooltip');
const ttTerm = tooltip.querySelector('.tt-term');
const ttShort = tooltip.querySelector('.tt-short');
const ttMore = tooltip.querySelector('.tt-more');
const modal = document.getElementById('modal');
const modalTerm = document.getElementById('modal-term');
const modalShort = document.getElementById('modal-short');
const modalLong = document.getElementById('modal-long');
const modalClose = document.getElementById('modal-close');

function openTermDetail(gid) {{
  const g = GLOSSARY[gid];
  if (!g) return;
  modalTerm.textContent = g.term;
  modalShort.textContent = g.short;
  modalLong.textContent = g.long;
  modal.classList.add('show');
  modal.setAttribute('aria-hidden', 'false');
}}

function closeModal() {{
  modal.classList.remove('show');
  modal.setAttribute('aria-hidden', 'true');
}}

document.addEventListener('mouseover', function(e) {{
  const el = e.target.closest('.term');
  if (!el) return;
  const gid = el.dataset.term;
  const g = GLOSSARY[gid];
  if (!g) return;
  ttTerm.textContent = g.term;
  ttShort.textContent = g.short;
  ttMore.textContent = g.long;
  ttMore.style.display = 'block';
  tooltip.classList.add('show');
  positionTooltip(e);
}});

document.addEventListener('mousemove', function(e) {{
  if (tooltip.classList.contains('show')) positionTooltip(e);
}});

document.addEventListener('mouseout', function(e) {{
  const el = e.target.closest('.term');
  if (!el) return;
  tooltip.classList.remove('show');
}});

document.addEventListener('click', function(e) {{
  const el = e.target.closest('.term');
  if (!el) return;
  openTermDetail(el.dataset.term);
}});

modalClose.addEventListener('click', closeModal);
modal.addEventListener('click', function(e) {{
  if (e.target === modal) closeModal();
}});
document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') {{
    if (modal.classList.contains('show')) closeModal();
    else if (document.getElementById('glossary-panel').classList.contains('open'))
      document.getElementById('glossary-panel').classList.remove('open');
  }}
  if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {{
    e.preventDefault();
    openGlossary();
    document.getElementById('gp-search').focus();
  }}
}});

function positionTooltip(e) {{
  const pad = 14;
  const tw = tooltip.offsetWidth;
  const th = tooltip.offsetHeight;
  let x = e.clientX + 18;
  let y = e.clientY + 18;
  if (x + tw + pad > window.innerWidth) x = e.clientX - tw - 18;
  if (y + th + pad > window.innerHeight) y = e.clientY - th - 18;
  tooltip.style.left = Math.max(pad, x) + 'px';
  tooltip.style.top = Math.max(pad, y) + 'px';
}}

// Glossary panel
const gpToggle = document.getElementById('gp-toggle');
const gpPanel = document.getElementById('glossary-panel');
const gpClose = document.getElementById('gp-close');
const gpSearch = document.getElementById('gp-search');
const gpList = document.getElementById('gp-list');

function openGlossary() {{ gpPanel.classList.add('open'); renderGlossary(''); }}
gpToggle.addEventListener('click', openGlossary);
gpClose.addEventListener('click', () => gpPanel.classList.remove('open'));

function renderGlossary(filter) {{
  const f = filter.toLowerCase().trim();
  const items = Object.values(GLOSSARY)
    .filter(g => !f || g.term.toLowerCase().includes(f) || g.short.toLowerCase().includes(f))
    .sort((a, b) => a.term.localeCompare(b.term));
  if (items.length === 0) {{
    gpList.innerHTML = '<div class="gp-empty">No matches.</div>';
    return;
  }}
  gpList.innerHTML = items.map(g =>
    `<div class="gp-item" data-id="${{g.id}}">
      <div class="gp-term">${{escapeHtml(g.term)}}</div>
      <div class="gp-short">${{escapeHtml(g.short)}}</div>
    </div>`
  ).join('');
  gpList.querySelectorAll('.gp-item').forEach(el => {{
    el.addEventListener('click', () => {{
      openTermDetail(el.dataset.id);
      gpPanel.classList.remove('open');
    }});
  }});
}}

gpSearch.addEventListener('input', e => renderGlossary(e.target.value));

function escapeHtml(s) {{
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}
</script>
</body>
</html>
"""


# ============================================================================
# MAIN
# ============================================================================

def build():
    en_qa = render_qa_html(QUESTIONS, "en")
    ua_qa = render_qa_html(QUESTIONS, "ua")

    en_html = page_html(
        lang="en",
        qa_html=en_qa,
        lang_label="English",
        other_lang_url="ua.html",
        other_lang_label="Українською",
    )
    ua_html = page_html(
        lang="uk",
        qa_html=ua_qa,
        lang_label="Українська",
        other_lang_url="index.html",
        other_lang_label="English",
    )

    (OUT_DIR / "index.html").write_text(en_html, encoding="utf-8")
    (OUT_DIR / "ua.html").write_text(ua_html, encoding="utf-8")

    print(f"Wrote: {OUT_DIR / 'index.html'}  ({len(en_html):,} bytes)")
    print(f"Wrote: {OUT_DIR / 'ua.html'}    ({len(ua_html):,} bytes)")
    print(f"Glossary: {len(GLOSSARY)} terms")
    print(f"Questions: {len(QUESTIONS)}")


if __name__ == "__main__":
    build()
