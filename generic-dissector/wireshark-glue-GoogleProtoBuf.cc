#include <iostream>
#include <string>

#include <google/protobuf/text_format.h>
#include <google/protobuf/unknown_field_set.h>
#include <google/protobuf/io/coded_stream.h>
#include <google/protobuf/io/zero_copy_stream.h>
#include <google/protobuf/io/zero_copy_stream_impl.h>

using namespace std;
using namespace google;
using namespace protobuf;


extern "C" {

#include <stdio.h>

char *mystrstr(const char *s1, const char *s2, int len1) {
    int len2;
    if (!(len2 = strlen(s2)))
        return (char *) s1;
    for (int i=0; i<len1-len2+1; ++s1,++i)
    {
        if (*s1 == *s2 && strncmp(s1, s2, len2) == 0)
        return (char *) s1;
    }
    return NULL;
}   

int wireshark_pb_add_GoogleProtoBuf(void* tree_root, void *tvb, 
    int item_id, char* msg_str);

/**
  * @param buf The message contents
  * @param buf_size The length of message contents in buf
  * @param tree_root The WireShark tree to which this message is to be added.
  * @param item_id Internal wireshark id to refer to this FT_NONE datatype.
  */
int wireshark_pb_process_GoogleProtoBuf(void* tree_root, int item_id, 
      void* tvb, void* buf, int buf_size) {

  string output_string;
  char * buf2 = mystrstr((char*)buf, "values:", buf_size);
  printf("tree_root: %d, item_id: %d, tvb: %d\n", tree_root, item_id, tvb);
  printf("Get buf: %d, %d\n", buf, buf_size);
  for(int i=0;i<buf_size;i++)
    printf("%02X", *(((char*)buf)+i));
  if(buf2)
  {
  printf("\nGet buf2:\n");
  for(int j=((char*)buf2)-((char*)buf);j<buf_size;j++)
    printf("%02X", *(((char*)buf)+j));

    buf_size -= ((char*)buf2)-((char*)buf) + strlen("values:");
    buf = (void*)(buf2 + strlen("values:"));
  printf("\nGet buf3: %d, %d\n", buf, buf_size);

  for(int i=0;i<buf_size;i++)
    printf("%02X", *(((char*)buf)+i));
}
  UnknownFieldSet unknown_fields;
  unknown_fields.ParseFromArray((const void*) buf, buf_size);
  if (TextFormat::PrintUnknownFieldsToString(unknown_fields, 
          &output_string)) {
    printf("\nPrintUnknownFieldsToString success!\n");
    //printf("%s\n", output_string.c_str());
    //char tmp_str[1000];
    //strncpy(tmp_str, output_string.c_str(), sizeof(tmp_str));
    //wireshark_pb_add_GoogleProtoBuf(tree_root, tvb, item_id, tmp_str);
    wireshark_pb_add_GoogleProtoBuf(tree_root, tvb, item_id, (char*)buf);
    return 0;

  } else {
    // This field is not parseable as a Message.  
    // So it is probably just a plain string.
    //return -1;
    printf("\nPrintUnknownFieldsToString fail!\n");
   wireshark_pb_add_GoogleProtoBuf(tree_root, tvb, item_id, (char*)buf);
  return 0;
  }
#if 0
  EmptyMessage msg;
  if (!msg.ParseFromArray((char *) buf, buf_size)) {
    cerr << "Failed to parse message." << endl;
    /*
    for (int i=0; i < buf_size; i++) {
      printf("%2x ", ((char *)buf)[i]);
    }
    */
    /*
    printf("buf size=%d\n", buf_size);
    printf("%s\n\n\n", buf);
    */
    return -1;
  }
#endif
}


}
