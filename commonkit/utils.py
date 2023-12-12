class Obfuscator:
    @classmethod
    def obfuscate(cls, s: str, char="*", cutoff=4, from_end=True):
        if not isinstance(s, str):
            raise ValueError("must provide strings to obfuscator")

        if not isinstance(cutoff, int):
            raise ValueError("cutoff must be an integer")

        if cutoff == 0:
            return s

        if cutoff < 0:
            raise ValueError(
                "must provide a positive cutoff, negative indices are not supported"
            )

        if len(s) <= cutoff:
            return char * len(s)

        if from_end:
            index = -cutoff - 1
        else:
            index = cutoff

        after_cutoff, before_cutoff = s[index:], s[:index]
        return (
            (before_cutoff + cutoff * char)
            if from_end
            else (char * cutoff + after_cutoff)
        )

    @classmethod
    def email(cls, e, char="*", cutoff=4, from_end=True):
        if "@" not in e:
            raise ValueError("email provided is not a valid email")

        host, domain = e.split("@")
        return cls.obfuscate(host, char, cutoff, from_end) + "@" + domain
