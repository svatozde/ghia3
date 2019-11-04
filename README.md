##Specifikace

- Aplikace musí přijímat na adrese `/` GitHub webhooky (metoda POST).
- Aplikace musí správně zpracovat https://developer.github.com/webhooks/[webhooky]
`issues` a `ping` ve formátu JSON.

Na `ping` aplikace správně odpoví dle dokumentace.

Na `issues` aplikace také správně odpoví dle dokumentace,
navíc přiřadí správné uživatele, případně nastaví správně štítek, dle konfiguračního souboru a zadání minulé úlohy.
Nastavení probíhá pouze, pokud byla událost vyvolána akcí `opened`, `edited`,
`transferred`, `reopened`, `assigned`, `unassigned`, `labeled`, `unlabeled`.

Aplikace musí podporovat zabezpečení pomocí webhook secret (viz dále).

Na adrese `/` se při požadavku GET bude nacházet jednoduchá HTML stránka,
ze které bude jasné, jaká pravidla platí a jaký uživatel bude akce provádět.
Uživatelské jméno se na stránce zobrazí podle použitého tokenu,
není zadrátované do kódu aplikace nebo šablony.

Musíte využít šablonu.
Nebudeme hodnotit vzhled stránky,
ale využijte HTML pro prezentaci informací.
Vydumpování Python slovníku do `<pre>` boxu není dostačující.
Pokud si nejste jisti, použijte zanořené seznamy (username: pravidla).
Na stránce musí být prezentován název fallback štítku, pokud je nastaven.

### Spouštění aplikace

Aplikace se musí dát spustit z kořenového adresáře repozitáře pomocí příkazu `flask run`
a to nastavením proměnné prostředí `FLASK_APP` na `ghia.py`.

[source,console]
$ export FLASK_APP=ghia.py
$ flask run

Zároveň je možné pomocí proměnné prostředí nastavit,
kde má aplikace hledat konfigurační soubor(y).

Pomocí proměnné `GHIA_CONFIG` je možné nastavit cestu k jednomu konfiguračnímu souboru,
nebo více souborům, oddělených dvojtečkou.

V konfiguračních souborech hledáte sekce `github` a `patterns` (případně také
nepovinný `fallback`). Chyby v konfiguraci se řeší identicky, jako v CLI aplikaci
(hlášky a návratový kód).

CLI aplikace z minulého týdne musí stále fungovat a testy z minula musí procházet.

Webová aplikace bude pracovat se strategií `append`. Dobrovolně můžete navíc
vyřešit nastavování strategie a dry-run například pomocí proměnných prostředí nebo dalších konfiguračních voleb.

Zabezpečení webhooku

Protože příjímání událostí z internetu může být riskantní,
nabízí GitHub možnost webhooky zabezpečit proti zneužiti.
Abyste rozpoznali, že vám událost poslal právě GitHub,
je ke každému requestu z GitHubu přiložená hlavička `X-Hub-Signature`, např:


X-Hub-Signature: sha1=0b861d9a594a4f421cabcdef75d5aefc46df8967

která vám říká,
že pokud použijete HMAC hexdigest s odpovídající hash funkcí a s klíčem,
který je uvedený v položce `secret`, na celé tělo requestu
a vámi spočítaný výsledek se shoduje s tím v hlavičce `X-Hub-Signature`,
tak tento request přišel z GitHubu, a můžete mu tedy veřit.

Více informací a příklad v Ruby je na
https://developer.github.com/webhooks/securing/[github securing].

Do konfigurančího souboru (sekce `github`) tedy přidejte položku `secret`.
Při nastavování webhooku na GitHubu použijte stejný secret jako při nasazování
aplikace.

#####Automatické testy

Testy z minula stále musí procházet.
Existuje i několik nových testů v souboru `test_web_smoke.py`.

Pro spuštění pouze nových testů můžete použít:

[source,console]
$ python -m pytest -v -k web test

Pro nové testy není třeba speciální setup z minula.

WARNING: Testy **netestují hlavní funkcionalitu aplikace**,
ale pouze přidružené věci, jako importovatelnost,
přítomnost usernamu na hlavní stránce, ping, ověření „secret“.
Ujistěte se, že vaše nasazená aplikace funguje, jak má.

Následuje text z minula, který stále platí:

