/* vi: set sw=4 ts=4: */
/*
 * Packet ops
 *
 * Rewrite by Russ Dill <Russ.Dill@asu.edu> July 2001
 *
 * Licensed under GPLv2, see file LICENSE in this source tree.
 */
/*
 * This code was stolen, pretty much, from busybox. :-)
 */
#include <stddef.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <netinet/in.h>
#include <netinet/if_ether.h>
#include <netpacket/packet.h>
#include "rawsocket.h"

static
uint16_t rawsocket_checksum(void *addr, int count)
{
  /* Compute Internet Checksum for "count" bytes
   * beginning at location "addr".
   */
  int32_t sum = 0;
  uint16_t *source = (uint16_t *) addr;
  
  while (count > 1)  {
    /*  This is the inner loop */
    sum += *source++;
    count -= 2;
  }
  
  /*  Add left-over byte, if any */
  if (count > 0) {
    /* Make sure that the left-over byte is added correctly both
     * with little and big endian hosts */
    uint16_t tmp = 0;
    *(uint8_t*)&tmp = *(uint8_t*)source;
    sum += tmp;
  }
  /*  Fold 32-bit sum to 16 bits */
  while (sum >> 16)
    sum = (sum & 0xffff) + (sum >> 16);
  
  return ~sum;
}

/* Construct a ip/udp header for a packet, send packet */
int rawsocket_udp_send_packet(const uint8_t *payload, int datalen, uint32_t source_nip, int source_port, uint32_t dest_nip, int dest_port, const uint8_t *dest_arp, int ifindex)
{
  struct sockaddr_ll dest_sll;
  struct ip_udp_dhcp_packet packet;
  int result = -1;
  int fd;
  
  fd = socket(PF_PACKET, SOCK_DGRAM, htons(ETH_P_IP));
  if (fd < 0 || datalen>DHCP_MAX_PKGSZ)
    return(result); // failure
  
  memset(&dest_sll, 0, sizeof(dest_sll));
  memset(&packet, 0, offsetof(struct ip_udp_dhcp_packet, data));
  memcpy(packet.data, payload, datalen);
  
  dest_sll.sll_family   = AF_PACKET;
  dest_sll.sll_protocol = htons(ETH_P_IP);
  dest_sll.sll_ifindex  = ifindex;
  dest_sll.sll_halen    = 6;
  memcpy(dest_sll.sll_addr, dest_arp, 6);
  
  if (bind(fd, (struct sockaddr *)&dest_sll, sizeof(dest_sll)) < 0)
    goto ret_close;

  packet.ip.protocol = IPPROTO_UDP;
  packet.ip.saddr    = source_nip;
  packet.ip.daddr    = dest_nip;
  packet.udp.source  = htons(source_port);
  packet.udp.dest    = htons(dest_port);
  /* size, excluding IP header: */
  packet.udp.len     = htons(UDP_DHCP_SIZE(datalen));
  /* for UDP checksumming, ip.len is set to UDP packet len */
  packet.ip.tot_len  = packet.udp.len;
  packet.udp.check   = rawsocket_checksum(&packet, IP_UDP_DHCP_SIZE(datalen));
  /* but for sending, it is set to IP packet len */
  packet.ip.tot_len  = htons(IP_UDP_DHCP_SIZE(datalen));
  packet.ip.ihl      = sizeof(packet.ip) >> 2;
  packet.ip.version  = IPVERSION;
  packet.ip.ttl      = IPDEFTTL;
  packet.ip.check    = rawsocket_checksum(&packet.ip, sizeof(packet.ip));
  
  result = sendto(fd, &packet, IP_UDP_DHCP_SIZE(datalen), /*flags:*/ 0, (struct sockaddr *) &dest_sll, sizeof(dest_sll));

ret_close:
  close(fd);
  return(result);
}
