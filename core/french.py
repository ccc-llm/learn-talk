"""法文動詞的現在式變化與過去分詞。

Mini-French 只用「現在式」，所以每個動詞需要六個人稱形式。
規則動詞用程式產生；不規則動詞列在 IRREGULAR 裡。

四組規則動詞：
    -er  : parler → parle / parles / parle / parlons / parlez / parlent
    -ir（第二組）: finir → finis / finis / finit / finissons / finissez / finissent
    -ir（第一組）: partir → pars / pars / part / partons / partez / partent
    -re  : vendre → vends / vends / vend / vendons / vendez / vendent

另外幾類需要特別處理：
    * 拼寫變化（acheter → achète、manger → mange、payer → paie、appeler → appelle）
    * 真正的不規則動詞（être、avoir、aller…）
"""

# ── 不規則動詞：lemma → (je, tu, il, nous, vous, ils) ────────────────────────
IRREGULAR: dict[str, tuple[str, str, str, str, str, str]] = {
    'être': ('suis', 'es', 'est', 'sommes', 'êtes', 'sont'),
    'avoir': ('ai', 'as', 'a', 'avons', 'avez', 'ont'),
    'aller': ('vais', 'vas', 'va', 'allons', 'allez', 'vont'),
    'venir': ('viens', 'viens', 'vient', 'venons', 'venez', 'viennent'),
    'faire': ('fais', 'fais', 'fait', 'faisons', 'faites', 'font'),
    'pouvoir': ('peux', 'peux', 'peut', 'pouvons', 'pouvez', 'peuvent'),
    'vouloir': ('veux', 'veux', 'veut', 'voulons', 'voulez', 'veulent'),
    'devoir': ('dois', 'dois', 'doit', 'devons', 'devez', 'doivent'),
    'savoir': ('sais', 'sais', 'sait', 'savons', 'savez', 'savent'),
    'voir': ('vois', 'vois', 'voit', 'voyons', 'voyez', 'voient'),
    'dire': ('dis', 'dis', 'dit', 'disons', 'dites', 'disent'),
    'prendre': ('prends', 'prends', 'prend', 'prenons', 'prenez', 'prennent'),
    'mettre': ('mets', 'mets', 'met', 'mettons', 'mettez', 'mettent'),
    'connaître': ('connais', 'connais', 'connaît', 'connaissons', 'connaissez', 'connaissent'),
    'recevoir': ('reçois', 'reçois', 'reçoit', 'recevons', 'recevez', 'reçoivent'),
    'partir': ('pars', 'pars', 'part', 'partons', 'partez', 'partent'),
    'sortir': ('sors', 'sors', 'sort', 'sortons', 'sortez', 'sortent'),
    'dormir': ('dors', 'dors', 'dort', 'dormons', 'dormez', 'dorment'),
    'mourir': ('meurs', 'meurs', 'meurt', 'mourons', 'mourez', 'meurent'),
    'naître': ('naîs', 'naîs', 'naît', 'naissons', 'naissez', 'naissent'),
    'rire': ('ris', 'ris', 'rit', 'risons', 'risez', 'rient'),
    'suivre': ('suis', 'suis', 'suit', 'suivons', 'suivez', 'suivent'),
    'boire': ('bois', 'bois', 'boit', 'buvons', 'buvez', 'boivent'),
    'envoyer': ('envoie', 'envoies', 'envoie', 'envoyons', 'envoyez', 'envoient'),
    'vivre': ('vis', 'vis', 'vit', 'vivons', 'vivez', 'vivent'),
    'falloir': ('faut', 'faut', 'faut', 'faut', 'faut', 'faut'),
    'pleuvoir': ('pleut', 'pleut', 'pleut', 'pleuvons', 'pleurez', 'pleuvent'),
    'tenir': ('tiens', 'tiens', 'tient', 'tenons', 'tenez', 'tiennent'),
    'écrire': ('écris', 'écris', 'écrit', 'écrivons', 'écrivez', 'écrivent'),
    'lire': ('lis', 'lis', 'lit', 'lisons', 'lisez', 'lisent'),
    'venir': ('viens', 'viens', 'vient', 'venons', 'venez', 'viennent'),
    'circuler': ('circule', 'circules', 'circule', 'circulons', 'circulez', 'circulent'),
}

# ── 拼寫變化：lemma → (je, tu, il, nous, vous, ils) ─────────────────────────
SPELLING: dict[str, tuple[str, str, str, str, str, str]] = {
    'manger': ('mange', 'manges', 'mange', 'mangeons', 'mangez', 'mangent'),
    'changer': ('change', 'changes', 'change', 'changeons', 'changez', 'changent'),
    'commencer': ('commence', 'commences', 'commence', 'commençons', 'commencez', 'commencent'),
    'acheter': ('achète', 'achètes', 'achète', 'achetons', 'achetez', 'achètent'),
    'préférer': ('préfère', 'préfères', 'préfère', 'préférons', 'préférez', 'préfèrent'),
    'appeler': ('appelle', 'appelles', 'appelle', 'appelons', 'appelez', 'appellent'),
    'payer': ('paie', 'paies', 'paie', 'payons', 'payez', 'paient'),
    'lever': ('lève', 'lèves', 'lève', 'levons', 'levez', 'lèvent'),
    'mener': ('mène', 'mènes', 'mène', 'menons', 'menez', 'mènent'),
    'créer': ('crée', 'crées', 'crée', 'créons', 'créez', 'créent'),
    'essayer': ('essaie', 'essaies', 'essaie', 'essayons', 'essayez', 'essaient'),
    'nettoyer': ('nettoie', 'nettoies', 'nettoie', 'nettoyons', 'nettoyez', 'nettoient'),
    'signer': ('signe', 'signes', 'signe', 'signons', 'signez', 'signent'),
    'répéter': ('répète', 'répètes', 'répète', 'répétons', 'répétez', 'répètent'),
    'arrêter': ('arrête', 'arrêtes', 'arrête', 'arrêtons', 'arrêtez', 'arrêtent'),
    'espérer': ('espère', 'espères', 'espère', 'espérons', 'espérez', 'espèrent'),
    'prévoir': ('prévois', 'prévois', 'prédit', 'prévois', 'prévez', 'prévoient'),
    'décrire': ('décris', 'décris', 'décrit', 'décrivons', 'décrivez', 'décrivent'),
    'conserver': ('conserve', 'conserves', 'conserve', 'conservons', 'conservez', 'conservent'),
    'organiser': ('organise', 'organises', 'organise', 'organisons', 'organisez', 'organisent'),
    'imaginer': ('imagine', 'imagines', 'imagine', 'imaginons', 'imaginez', 'imaginent'),
    'présenter': ('présente', 'présentes', 'présente', 'présentons', 'présentez', 'présentent'),
    'préparer': ('prépare', 'prépares', 'prépare', 'préparons', 'préparez', 'préparent'),
    'réparer': ('répare', 'répares', 'répare', 'réparons', 'réparez', 'réparent'),
    'visiter': ('visite', 'visites', 'visite', 'visitons', 'visitez', 'visitent'),
    'rencontrer': ('rencontre', 'rencontres', 'rencontre', 'rencontrons', 'rencontrez', 'rencontrent'),
    'commander': ('commande', 'commandes', 'commande', 'commandons', 'commandez', 'commandent'),
    'utiliser': ('utilise', 'utilises', 'utilise', 'utilisons', 'utilisez', 'utilisent'),
    'continuer': ('continue', 'continues', 'continue', 'continuons', 'continuez', 'continuent'),
    'expliquer': ('explique', 'expliques', 'explique', 'expliquons', 'expliquez', 'expliquent'),
    'travailler': ('travaille', 'travailles', 'travaille', 'travaillons', 'travaillez', 'travaillent'),
    'étudier': ('étudie', 'étudies', 'étudie', 'étudions', 'étudiez', 'étudient'),
    'aider': ('aide', 'aides', 'aide', 'aidons', 'aidez', 'aident'),
    'habiter': ('habite', 'habites', 'habite', 'habitons', 'habitez', 'habitent'),
    'inviter': ('invite', 'invites', 'invite', 'invitons', 'invitez', 'invitent'),
    'saluer': ('salue', 'salues', 'salue', 'salons', 'saluez', 'saluent'),
    'partager': ('partage', 'partages', 'partage', 'partageons', 'partagez', 'partagent'),
    'voyager': ('voyage', 'voyages', 'voyage', 'voyageons', 'voyagez', 'voyagent'),
    'fabriquer': ('fabrique', 'fabriques', 'fabrique', 'fabriquons', 'fabriquez', 'fabriquent'),
    'cuisiner': ('cuisine', 'cuisines', 'cuisine', 'cuisinons', 'cuisinez', 'cuisinent'),
    'charger': ('charge', 'charges', 'charge', 'chargeons', 'chargez', 'chargent'),
    'lancer': ('lance', 'lances', 'lance', 'lançons', 'lancez', 'lancen'),
    'gagner': ('gagne', 'gagnes', 'gagne', 'gagnons', 'gagnez', 'gagnent'),
    'jouer': ('joue', 'joues', 'joue', 'jouons', 'jouez', 'jouent'),
    'chanter': ('chante', 'chantes', 'chante', 'chantons', 'chantez', 'chantent'),
    'danser': ('danse', 'danses', 'danse', 'dansons', 'dansez', 'dansent'),
    'pleurer': ('pleure', 'pleures', 'pleure', 'pleurons', 'pleurez', 'pleurent'),
    'toucher': ('touche', 'touches', 'touche', 'touchons', 'touchez', 'touchent'),
    'sentir': ('sens', 'sens', 'sent', 'sentons', 'sentez', 'sentent'),
    'aimer': ('aime', 'aimes', 'aime', 'aimons', 'aimez', 'aiment'),
    'penser': ('pense', 'penses', 'pense', 'pensons', 'pensez', 'pensent'),
    'demander': ('demande', 'demandes', 'demande', 'demandons', 'demandez', 'demandent'),
    'donner': ('donne', 'donnes', 'donne', 'donnons', 'donnez', 'donnent'),
    'répondre': ('réponds', 'réponds', 'répond', 'répondons', 'répondez', 'répondent'),
    'entendre': ('entends', 'entends', 'entend', 'entendons', 'entendez', 'entendent'),
    'écouter': ('écoute', 'écoutes', 'écoute', 'écoutons', 'écoutez', 'écoutent'),
    'regarder': ('regarde', 'regardes', 'regarde', 'regardons', 'regardez', 'regardent'),
    'chercher': ('cherche', 'cherches', 'cherche', 'cherchons', 'cherchez', 'cherchent'),
    'trouver': ('trouve', 'trouves', 'trouve', 'trouvons', 'trouvez', 'trouvent'),
    'montrer': ('montre', 'montres', 'montre', 'montrons', 'montrez', 'montrent'),
    'oublier': ('oublie', 'oublies', 'oublie', 'oublions', 'oubliez', 'oublient'),
    'laver': ('lave', 'laves', 'lave', 'lavons', 'lavez', 'lavent'),
    'couper': ('coupe', 'coupes', 'coupe', 'coupons', 'coupez', 'coupent'),
    'passer': ('passe', 'passes', 'passe', 'passons', 'passez', 'passent'),
    'rendre': ('rends', 'rends', 'rend', 'rendons', 'rendez', 'rendent'),
    'attendre': ('attends', 'attends', 'attend', 'attendons', 'attendez', 'attendent'),
    'comprendre': ('comprends', 'comprends', 'comprend', 'comprenons', 'comprenez', 'comprennent'),
    'apprendre': ('apprends', 'apprends', 'apprend', 'apprenons', 'apprenez', 'apprennent'),
    'prendre': ('prends', 'prends', 'prend', 'prenons', 'prenez', 'prennent'),
    'reprendre': ('reprends', 'reprends', 'reprend', 'reprenons', 'reprenez', 'reprennent'),
    'survivre': ('survis', 'survis', 'survit', 'survivons', 'survivez', 'survivent'),
    'recevoir': ('reçois', 'reçois', 'reçoit', 'recevons', 'recevez', 'reçoivent'),
    'vendre': ('vends', 'vends', 'vend', 'vendons', 'vendez', 'vendent'),
    'conduire': ('conduis', 'conduis', 'conduit', 'conduisons', 'conduisez', 'conduisent'),
    'produire': ('produis', 'produis', 'produit', 'produisons', 'produisez', 'produisent'),
    'réagir': ('réagis', 'réagis', 'réagit', 'réagissons', 'réagissez', 'réagissent'),
    'obéir': ('obéis', 'obéis', 'obéit', 'obéissons', 'obéissez', 'obéissent'),
    'grandir': ('grandis', 'grandis', 'grandit', 'grandissons', 'grandissez', 'grandissent'),
    'finir': ('finis', 'finis', 'finit', 'finissons', 'finissez', 'finissent'),
    'réussir': ('réussis', 'réussis', 'réussit', 'réussissons', 'réussissez', 'réussissent'),
    'choisir': ('choisis', 'choisis', 'choisit', 'choisissons', 'choisissez', 'choisissent'),
    'échouer': ('échoue', 'échoues', 'échoue', 'échouons', 'échouez', 'échouent'),
    'décider': ('décide', 'décides', 'décide', 'décidons', 'décidez', 'décident'),
    'arriver': ('arrive', 'arrives', 'arrive', 'arrivons', 'arrivez', 'arrivent'),
    'entrer': ('entre', 'entres', 'entre', 'entrons', 'entrez', 'entrent'),
    'monter': ('monte', 'montes', 'monte', 'montons', 'montez', 'montent'),
    'descendre': ('descends', 'descends', 'descend', 'descendons', 'descendez', 'descendent'),
    'tomber': ('tombe', 'tombes', 'tombe', 'tombons', 'tombez', 'tombent'),
    'rester': ('reste', 'restes', 'reste', 'restons', 'restez', 'restent'),
    'ouvrir': ('ouvre', 'ouvres', 'ouvre', 'ouvrons', 'ouvrez', 'ouvrent'),
    'fermer': ('ferme', 'fermes', 'ferme', 'fermons', 'fermez', 'ferment'),
    'acheter': ('achète', 'achètes', 'achète', 'achetons', 'achetez', 'achètent'),
    'payer': ('paie', 'paies', 'paie', 'payons', 'payez', 'paient'),
    'envoyer': ('envoie', 'envoies', 'envoie', 'envoyons', 'envoyez', 'envoient'),
    'voir': ('vois', 'vois', 'voit', 'voyons', 'voyez', 'voient'),
    'naître': ('naîs', 'naîs', 'naît', 'naissons', 'naissez', 'naissent'),
    'dormir': ('dors', 'dors', 'dort', 'dormons', 'dormez', 'dorment'),
    'mourir': ('meurs', 'meurs', 'meurt', 'mourons', 'mourez', 'meurent'),
    'sortir': ('sors', 'sors', 'sort', 'sortons', 'sortez', 'sortent'),
    'partir': ('pars', 'pars', 'part', 'partons', 'partez', 'partent'),
    'suivre': ('suis', 'suis', 'suit', 'suivons', 'suivez', 'suivent'),
    'rire': ('ris', 'ris', 'rit', 'risons', 'risez', 'rient'),
    'boire': ('bois', 'bois', 'boit', 'buvons', 'buvez', 'boivent'),
    'faire': ('fais', 'fais', 'fait', 'faisons', 'faites', 'font'),
    'dire': ('dis', 'dis', 'dit', 'disons', 'dites', 'disent'),
    'mettre': ('mets', 'mets', 'met', 'mettons', 'mettez', 'mettent'),
    'prendre': ('prends', 'prends', 'prend', 'prenons', 'prenez', 'prennent'),
    'avoir': ('ai', 'as', 'a', 'avons', 'avez', 'ont'),
    'être': ('suis', 'es', 'est', 'sommes', 'êtes', 'sont'),
    'aller': ('vais', 'vas', 'va', 'allons', 'allez', 'vont'),
    'venir': ('viens', 'viens', 'vient', 'venons', 'venez', 'viennent'),
    'pouvoir': ('peux', 'peux', 'peut', 'pouvons', 'pouvez', 'peuvent'),
    'vouloir': ('veux', 'veux', 'veut', 'voulons', 'voulez', 'veulent'),
    'devoir': ('dois', 'dois', 'doit', 'devons', 'devez', 'doivent'),
    'savoir': ('sais', 'sais', 'sait', 'savons', 'savez', 'savent'),
    'connaître': ('connais', 'connais', 'connaît', 'connaissons', 'connaissez', 'connaissent'),
    'recevoir': ('reçois', 'reçois', 'reçoit', 'recevons', 'recevez', 'reçoivent'),
    'envoyer': ('envoie', 'envoies', 'envoie', 'envoyons', 'envoyez', 'envoient'),
    'vivre': ('vis', 'vis', 'vit', 'vivons', 'vivez', 'vivent'),
    'tenir': ('tiens', 'tiens', 'tient', 'tenons', 'tenez', 'tiennent'),
    'écrire': ('écris', 'écris', 'écrit', 'écrivons', 'écrivez', 'écrivent'),
    'lire': ('lis', 'lis', 'lit', 'lisons', 'lisez', 'lisent'),
}

# ── 反身動詞 ─────────────────────────────────────────────────────────────────
REFLEXIVE = {
    'se lever', 'se coucher', 'se réveiller', 'se laver', "s'habiller",
    'se promener', 'se reposer', 'se dépêcher',
}

# 反身代詞：主詞 → 反身代詞
REFLEXIVE_PRONOUNS = {
    'je': 'me', 'tu': 'te', 'il': 'se', 'elle': 'se', 'on': 'se',
    'nous': 'nous', 'vous': 'vous', 'ils': 'se', 'elles': 'se',
}

# 反身動詞的過去分詞（不規則）
REFLEXIVE_PARTICIPLES = {
    'se lever': 'levé', 'se coucher': 'couché', 'se réveiller': 'réveillé',
    'se laver': 'lavé', "s'habiller": 'habillé', 'se promener': 'promené',
    'se reposer': 'reposé', 'se dépêcher': 'dépêché',
}


def verb_class(w: str) -> str:
    """判斷動詞屬於哪一組。"""
    if w.endswith('er'):
        return 'er'
    if w.endswith('ir'):
        return 'ir2' if len(w) > 4 and w[-3] in 'nt' else 'ir1'
    if w.endswith('re'):
        return 're'
    return 'er'


def present_forms(w: str) -> tuple[str, str, str, str, str, str]:
    """規則動詞的現在式六式。"""
    cls = verb_class(w)
    if cls == 'er':
        stem = w[:-2]
        return (stem + 'e', stem + 'es', stem + 'e',
                stem + 'ons', stem + 'ez', stem + 'ent')
    if cls == 'ir2':
        stem = w[:-2]
        return (stem + 'is', stem + 'is', stem + 'it',
                stem + 'issons', stem + 'issez', stem + 'issent')
    if cls == 'ir1':
        stem = w[:-2]
        if stem.endswith('e'):
            return (stem[:-1] + 's', stem[:-1] + 's', stem[:-1] + 's',
                    stem + 'ons', stem + 'ez', stem + 'ent')
        return (stem + 's', stem + 's', stem + 't',
                stem + 'ons', stem + 'ez', stem + 'ent')
    stem = w[:-2]
    return (stem + 's', stem + 's', stem + 't',
            stem + 'ons', stem + 'ez', stem + 'ent')


def conjugation(w: str) -> tuple[str, str, str, str, str, str]:
    """動詞的現在式六式（不規則優先）。"""
    if w in IRREGULAR:
        return IRREGULAR[w]
    if w in SPELLING:
        return SPELLING[w]
    return present_forms(w)


def past_participle(w: str, irr: list[str] | None = None) -> str:
    """過去分詞（不規則表優先）。"""
    if irr:
        return irr[0]
    if w in REFLEXIVE_PARTICIPLES:
        return REFLEXIVE_PARTICIPLES[w]
    cls = verb_class(w)
    if cls == 'er':
        # parler → parlé, manger → mangé
        return w[:-2] + 'é'
    if cls == 'ir2':
        return w[:-2] + 'i'
    if cls == 'ir1':
        return w + 'i'
    if cls == 're':
        return w[:-2] + 'u'
    return w
