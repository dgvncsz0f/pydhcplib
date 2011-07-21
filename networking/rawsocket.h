/*
 * Russ Dill <Russ.Dill@asu.edu> September 2001
 * Rewritten by Vladimir Oleynik <dzo@simtreas.ru> (C) 2003
 *
 * Licensed under GPLv2 or later, see file LICENSE in this source tree.
 */
/*
 * This code was stolen, pretty much, from busybox. :-)
 */
#ifndef PYDHCPLIB_RAWSOCKET_H
#define PYDHCPLIB_RAWSOCKET_H 1

#include <netinet/udp.h>
#include <netinet/ip.h>

#ifndef DHCP_MAX_PKGSZ
#define DHCP_MAX_PKGSZ (1500 - sizeof(struct iphdr) - sizeof(struct udphdr))
#endif

struct ip_udp_dhcp_packet
{
	struct iphdr ip;
	struct udphdr udp;
	uint8_t data[DHCP_MAX_PKGSZ];
};

/* Construct a ip/udp header for a packet, send packet */
int rawsocket_udp_send_packet(const uint8_t *payload, int datalen, uint32_t source_nip, int source_port, uint32_t dest_nip, int dest_port, const uint8_t *dest_arp, int ifindex);

#define IP_UDP_DHCP_SIZE(payloadsz) (sizeof(struct ip_udp_dhcp_packet)-DHCP_MAX_PKGSZ+payloadsz)
#define UDP_DHCP_SIZE(payloadsz) (sizeof(struct udphdr)+payloadsz)

#endif
