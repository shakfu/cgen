"""
Typedef of a struct then declare a variable of that struct with initializer.

Style:
- new-line after opening brace

"""
import cfile

from pydantic import BaseModel


C = cfile.CFactory()
code = C.sequence()

class Person(BaseModel):
    name: str
    age: int

    def to_c(self, C, code):
        d = self.schema()
        struct_name = d['title']
        members = []
        for p in d['properties']:
            prop = d['properties'][p]
            members.append(C.struct_member(p, prop['type']))
        struct = C.struct('_'+struct_name.lower(), members=members)
        struct_type = C.typedef(struct_name, C.declaration(struct))
        code.append(C.statement(C.declaration(struct_type)))
        code.append(C.blank())
        code.append(C.statement(C.declaration(C.variable("instance", struct_type), [self.name, self.age])))

p = Person(name='sa', age=10)
p.to_c(C, code)

writer = cfile.Writer(cfile.StyleOptions(break_before_braces=cfile.BreakBeforeBraces.ATTACH))
print(writer.write_str(code))
