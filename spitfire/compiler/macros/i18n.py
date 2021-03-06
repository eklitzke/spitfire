import sys

import cStringIO as StringIO

from spitfire.compiler import analyzer
from spitfire.compiler.ast import *
from spitfire.compiler.visitor import print_tree

import spitfire.util


# generate a reasonable substitute name from a raw placeholder node
def make_placeholder_name(placeholder_node):
  node_type = type(placeholder_node.expression)
  placeholder_name = ''
  if node_type is PlaceholderNode:
    placeholder_name = placeholder_node.expression.name
  elif node_type is CallFunctionNode:
    placeholder = placeholder_node.expression.expression
    if type(placeholder) is PlaceholderNode:
      placeholder_name = placeholder.name

  placeholder_name = placeholder_name.upper()
  return placeholder_name

  
# create a translated version of the raw_msg while allowing placeholder
# expressions to pass through correctly
def make_i18n_message(raw_msg, macro_ast):
  # top should be a fragment and due to the limited syntax, we can more or
  # less scan this one level of nodes -- there are no nested i18n sections yet
  output = StringIO.StringIO()
  for i, n in enumerate(macro_ast.child_nodes):
    #print i, type(n), "start", n.start, "end", n.end
    #print "raw:", "'%s'" % raw_msg[n.start:n.end]
    
    if isinstance(n, PlaceholderSubstitutionNode):
      raw_placeholder_expression = raw_msg[n.start:n.end]
      #output.write(make_placeholder_name(n))
      output.write(raw_placeholder_expression)
    else:
      output.write(spitfire.util.i18n_mangled_message(n.value))
  return output.getvalue()


def macro_i18n(macro_node, arg_map, compiler):
  # fixme: parse the parameter list into something usable
  # macro_node.parameter_list

  # generate a fake translation for now to verify this is working
  # most apps will have to stub this part out somehow i think
  macro_content_ast = spitfire.compiler.util.parse(macro_node.value,
                                                   'i18n_goal')
  i18n_msg = make_i18n_message(macro_node.value, macro_content_ast)
  i18n_msg_utf8 = i18n_msg.encode('utf-8')
  #print "macro_content_ast"
  #print "orginal:", macro_node.value
  #print "i18n:", i18n_msg_utf8
  #print_tree(macro_content_ast)
  return i18n_msg_utf8

def macro_function_i18n(call_node, arg_map, compiler):
  # generate a fake translation for now to verify this is working
  # most apps will have to stub this part out somehow i think
  # in the context of a function, the goal is to replace a function with a
  # translated literal string. we have to do some shenanigans since Spitfire
  # doesn't parse repr(unicode)
  msg_arg_node = call_node.arg_list.parg_list[0]
  if not isinstance(msg_arg_node, LiteralNode):
    raise analyzer.SemanticAnalyzerError(
      '$i18n argument "%s" must be a string literal' % msg_arg_node)
  i18n_msg = spitfire.util.i18n_mangled_message(msg_arg_node.value)
  i18n_msg_utf8 = i18n_msg.encode('utf-8')
  return u"'%s'" % i18n_msg.replace("'", "\\'")
  
