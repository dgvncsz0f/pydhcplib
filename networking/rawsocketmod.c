/* Copyright (c) 2011, Diego Souza                                                 */
/* All rights reserved.                                                            */
                                                                                   
/* Redistribution and use in source and binary forms, with or without              */
/* modification, are permitted provided that the following conditions are met:     */
                                                                                   
/*   * Redistributions of source code must retain the above copyright notice,      */
/*     this list of conditions and the following disclaimer.                       */
/*   * Redistributions in binary form must reproduce the above copyright notice,   */
/*     this list of conditions and the following disclaimer in the documentation   */
/*     and/or other materials provided with the distribution.                      */
/*   * Neither the name of the <ORGANIZATION> nor the names of its contributors    */
/*     may be used to endorse or promote products derived from this software       */
/*     without specific prior written permission.                                  */

/* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND */
/* ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED   */
/* WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE          */
/* DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE    */
/* FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL      */
/* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR      */
/* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER      */
/* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,   */
/* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE   */
/* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.            */

#include <Python.h>
#include "rawsocket.h"

static
PyObject *python_rawsocket_udp_send_packet(PyObject *self, PyObject *args);

static 
PyMethodDef rawsocket_methods[] = {
  {"udp_send_packet",  python_rawsocket_udp_send_packet, METH_VARARGS, "Sends an udp packet using raw socket"},
  {NULL, NULL, 0, NULL}
};

static
PyObject *python_rawsocket_udp_send_packet(PyObject *self, PyObject *args)
{
  char *payload, *hwaddr;
  int payloadlen, hwaddrlen;
  unsigned int source_nip, source_port;
  unsigned int dest_nip, dest_port;
  int ifindex;

  if (! PyArg_ParseTuple(args, "z#IIIIz#i", &payload, &payloadlen, &source_nip, &source_port, &dest_nip, &dest_port, &hwaddr, &hwaddrlen, &ifindex))
    return(NULL);

  if (hwaddrlen != 6)
    Py_RETURN_FALSE;

  int result = rawsocket_udp_send_packet( (const uint8_t*) payload,
                                          payloadlen, 
                                          (uint32_t) source_nip,
                                          (uint32_t) source_port,
                                          (uint32_t) dest_nip,
                                          (uint32_t) dest_port,
                                          (const uint8_t*) hwaddr,
                                          ifindex
                                        );
  if (result == 0)
    Py_RETURN_TRUE;
  else
    Py_RETURN_FALSE;
}

PyMODINIT_FUNC
init_rawsocket(void)
{
  (void) Py_InitModule("_rawsocket", rawsocket_methods);
}
