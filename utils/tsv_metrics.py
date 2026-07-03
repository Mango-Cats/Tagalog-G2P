import unicodedata
from collections import Counter, defaultdict
from alignment import align_trxn

_SKIP = frozenset('ˈˌ.')
_TIE_BAR = '͡'  # ͡  COMBINING DOUBLE INVERTED BREVE
_LENGTH   = 'ː'  # ː  MODIFIER LETTER TRIANGULAR COLON


def tokenize_ipa(ipa_str):
    """Tokenize an IPA string into a list of phone symbols.

    Strips stress markers (ˈ ˌ) and syllable boundaries (.), keeps
    combining diacritics (e.g. n̪ t̪), length marks (aː), and tie-bar
    affricates (d͡ʒ) as single tokens.
    """
    phones = []
    current = None
    grab_next = False  # True immediately after a tie-bar

    for ch in ipa_str:
        if ch in _SKIP:
            if current is not None:
                phones.append(current)
                current = None
            grab_next = False
            continue

        # Combining marks (Mn/Mc/Me) and the length modifier attach to current phone.
        is_modifier = unicodedata.category(ch).startswith('M') or ch == _LENGTH

        if is_modifier:
            if current is not None:
                current += ch
            if ch == _TIE_BAR:
                grab_next = True  # next base char belongs to this phone
        elif grab_next:
            # Base char that follows a tie bar completes the affricate.
            if current is not None:
                current += ch
            grab_next = False
        else:
            if current is not None:
                phones.append(current)
            current = ch

    if current is not None:
        phones.append(current)

    return phones


def load_tsv(path, skip_multiword=True):
    """Load a G2P TSV (word TAB IPA) into {word: [phones]}.

    Multi-word grapheme entries (containing a space) are skipped by default
    because Phonetisaurus operates on single words.
    """
    data = {}
    with open(path, encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 2:
                continue
            word, ipa = parts[0].strip(), parts[1].strip()
            if skip_multiword and ' ' in word:
                continue
            phones = tokenize_ipa(ipa)
            if phones:
                data[word] = phones
    return data


def compute_per_wer(ref, hyp):
    """Compute PER and WER given reference and hypothesis dicts {word: [phones]}.

    Only words present in both dicts are evaluated.

    Returns a dict with keys:
        per         – phone error rate  (edit distance / ref phones)
        wer         – word error rate   (wrong words / total words)
        n_words     – words evaluated
        n_correct   – words with zero phone errors
        n_ref_phones – total reference phones
        n_edit       – total phone edit distance
    """
    total_ref_phones = 0
    total_edit = 0
    n_correct = 0
    n_words = 0

    for word, ref_phones in ref.items():
        if word not in hyp:
            continue
        hyp_phones = hyp[word]
        n_words += 1
        total_ref_phones += len(ref_phones)
        edit = align_trxn(ref_phones, hyp_phones)[2]
        total_edit += edit
        if edit == 0:
            n_correct += 1

    per = total_edit / total_ref_phones if total_ref_phones > 0 else 0.0
    wer = 1.0 - (n_correct / n_words) if n_words > 0 else 0.0

    return {
        'per':          per,
        'wer':          wer,
        'n_words':      n_words,
        'n_correct':    n_correct,
        'n_ref_phones': total_ref_phones,
        'n_edit':       total_edit,
    }


_MAX_EXAMPLES = 5


def collect_errors(ref, hyp):
    """Collect substitution, deletion, and insertion statistics across all word pairs.

    Returns a dict with:
        n_sub, n_del, n_ins          – total counts per error type
        sub_ref_counter              – Counter of ref phones involved in substitutions
        sub_hyp_counter              – Counter of hyp phones involved in substitutions
        del_counter                  – Counter of deleted ref phones
        ins_counter                  – Counter of inserted hyp phones
        sub_pair_counter             – Counter of (ref_phone, hyp_phone) substitution pairs
        sub_ref_examples             – {phone: [example dicts]} up to _MAX_EXAMPLES each
        sub_hyp_examples             – {phone: [example dicts]} up to _MAX_EXAMPLES each
        del_examples                 – {phone: [example dicts]} up to _MAX_EXAMPLES each
        ins_examples                 – {phone: [example dicts]} up to _MAX_EXAMPLES each
        sub_pair_examples            – {(r,h): [example dicts]} up to _MAX_EXAMPLES each

    Each example dict: {'word': str, 'ref': str, 'hyp': str, 'op': str}
    Only words present in both ref and hyp are evaluated.
    """
    n_sub = n_del = n_ins = 0
    sub_ref_counter  = Counter()
    sub_hyp_counter  = Counter()
    del_counter      = Counter()
    ins_counter      = Counter()
    sub_pair_counter = Counter()

    sub_ref_examples  = defaultdict(list)
    sub_hyp_examples  = defaultdict(list)
    del_examples      = defaultdict(list)
    ins_examples      = defaultdict(list)
    sub_pair_examples = defaultdict(list)

    for word, ref_phones in ref.items():
        if word not in hyp:
            continue
        hyp_phones = hyp[word]
        _, _, _, ops = align_trxn(ref_phones, hyp_phones)

        base = {
            'word': word,
            'ref':  ' '.join(ref_phones),
            'hyp':  ' '.join(hyp_phones),
        }

        for (r, h) in ops:
            if r == '*':
                n_ins += 1
                ins_counter[h] += 1
                if len(ins_examples[h]) < _MAX_EXAMPLES:
                    ins_examples[h].append({**base, 'op': f'ins({h})'})
            elif h == '*':
                n_del += 1
                del_counter[r] += 1
                if len(del_examples[r]) < _MAX_EXAMPLES:
                    del_examples[r].append({**base, 'op': f'del({r})'})
            elif r != h:
                n_sub += 1
                sub_ref_counter[r] += 1
                sub_hyp_counter[h] += 1
                sub_pair_counter[(r, h)] += 1
                if len(sub_ref_examples[r]) < _MAX_EXAMPLES:
                    sub_ref_examples[r].append({**base, 'op': f'sub({r}→{h})'})
                if len(sub_hyp_examples[h]) < _MAX_EXAMPLES:
                    sub_hyp_examples[h].append({**base, 'op': f'sub({r}→{h})'})
                pair = (r, h)
                if len(sub_pair_examples[pair]) < _MAX_EXAMPLES:
                    sub_pair_examples[pair].append({**base, 'op': f'sub({r}→{h})'})

    return {
        'n_sub': n_sub,
        'n_del': n_del,
        'n_ins': n_ins,
        'sub_ref_counter':  sub_ref_counter,
        'sub_hyp_counter':  sub_hyp_counter,
        'del_counter':      del_counter,
        'ins_counter':      ins_counter,
        'sub_pair_counter': sub_pair_counter,
        'sub_ref_examples':  dict(sub_ref_examples),
        'sub_hyp_examples':  dict(sub_hyp_examples),
        'del_examples':      dict(del_examples),
        'ins_examples':      dict(ins_examples),
        'sub_pair_examples': dict(sub_pair_examples),
    }


# Tagalog vowel-height mergers: o~u and e~i are historically allophonic and are a
# recurring G2P failure mode. Each group is the set of base vowels that get confused.
_DEFAULT_VOWEL_GROUPS = {"o/u": {"o", "u"}, "e/i": {"e", "i"}}


def _base_vowel(ph):
    """Strip combining marks and the length modifier (ː) so oː/õ fold to o."""
    return ''.join(
        c for c in ph
        if not unicodedata.category(c).startswith('M') and c != _LENGTH
    )


def vowel_confusion(ref, hyp, groups=None):
    """Count directed vowel-height substitutions per group (e.g. o↔u, e↔i).

    Reuses collect_errors(); a substitution (r→h) counts for a group when the
    base vowels of r and h are both in that group and differ. Length/diacritic
    variants (oː, õ) fold to their base vowel via _base_vowel.

    Args:
        ref, hyp: dicts of {word: [phones]} (only words in both are scored).
        groups:   {label: set of base vowels}; defaults to o/u and e/i.

    Returns {label: {"count": int,
                     "by_pair": Counter{(ref_phone, hyp_phone): n},
                     "examples": [example dicts],
                     "rate": float}}   where rate = count / total substitutions.
    """
    if groups is None:
        groups = _DEFAULT_VOWEL_GROUPS

    err = collect_errors(ref, hyp)
    n_sub = err['n_sub']

    result = {}
    for label, vowels in groups.items():
        by_pair = Counter()
        examples = []
        for (r, h), c in err['sub_pair_counter'].items():
            rb, hb = _base_vowel(r), _base_vowel(h)
            if rb in vowels and hb in vowels and rb != hb:
                by_pair[(r, h)] += c
                examples.extend(err['sub_pair_examples'].get((r, h), []))
        count = sum(by_pair.values())
        result[label] = {
            'count':    count,
            'by_pair':  by_pair,
            'examples': examples,
            'rate':     count / n_sub if n_sub else 0.0,
        }
    return result
