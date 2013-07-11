#include <stdio.h>
#include <string.h>
#ifdef __LINUX__
#include <dirent.h>
#endif
#ifdef __WIN32__
#include <dir.h>
#endif

#define MAX_LINE_LEN 4096
#define MAX_VAR_LEN 128
#define MAX_FILENAME 512
#define MAX_TYPE_COUNT 128 

enum data_type {
  BOOL = 0,
  INT,
  STRING,
  FLOAT,
  ARR_BOOL,
  ARR_INT,
  ARR_STRING,
  ARR_FLOAT,
  DATE,
  TYPE_COUNT
};

static const char *data_type[] = {
  "bool", "int", "string", "double", "bool[]", "int[]",
  "string[]", "double[]", "date"
};

static const char *data_type_java[] = {
  "boolean", "int", "String", "double", "boolean[]", "int[]",
  "String[]", "double[]", "String"
};

static const char *default_value[] = {
  "false", "0", "\"\"", "0", "", "", "", "", "\"\""
};

static inline int 
get_type(const char *);

static FILE *
open_file(const char *, const char *m);

static void
proc_head(FILE *, FILE *);

static void
proc_data(FILE *, FILE *);

static void
proc(FILE *, FILE *, FILE *);

static char class_name[MAX_FILENAME];
/*
 *the format of hf: filename.zk
 */
static void
get_classname(const char *hf) {
  const char *name_beg = strrchr(hf, '/'), *msname_beg = strrchr(hf, '\\');
  if (name_beg == NULL || (msname_beg != NULL && name_beg < msname_beg))
    name_beg = msname_beg;

  if (name_beg == NULL)
    name_beg = hf - 1;
  name_beg += 1;
  memcpy(class_name, name_beg, strlen(name_beg) - 3);
  class_name[strlen(name_beg) - 3] = '\0';
#ifdef DEBUG
  printf("classname: %s\n", class_name);
#endif
}

/*
 * the value of suffix: ".java"
 */
static char *
get_filename(const char *outdir, const char *suffix)
{
  static char fn[MAX_FILENAME];
  int fn_idx = strlen(outdir);
  int outdir_len = strlen(outdir);
  memcpy(fn, outdir, outdir_len);
  char file_sep = '\\';
#ifdef __LINUX__
  file_sep = '/';
#endif
  fn[fn_idx++] = file_sep;
  memcpy(fn + fn_idx, class_name, strlen(class_name));
  fn_idx = fn_idx + strlen(class_name);
  memcpy(fn + fn_idx, suffix, strlen(suffix));
  fn[fn_idx + strlen(suffix)] = '\0';
#ifdef DEBUG
  printf("output file name: %s\n", fn);
#endif
  return fn;
}

inline static FILE *
open_headerfile(const char *fn)
{
  get_classname(fn);
  FILE *ans = open_file(fn, "r");
  return ans;
}

inline static FILE *
open_datafile(const char *headerfn)
{
  char datafilename[256];
  strcpy(datafilename, headerfn);
  datafilename[strlen(headerfn) - 2] = 'd';
  FILE *ans = open_file(datafilename, "r");
  return ans;
}

inline static FILE *
open_targetfile(const char *output_dir)
{
  return open_file(get_filename(output_dir, ".java"), "w");
}

inline static void
proc_one(char *fn, const char *output_dir)
{
  FILE *fh, *fd, *foutj;
  if ((fh = open_headerfile(fn)) == NULL) 
    return;

  if ((fd = open_datafile(fn)) == NULL) {
    fclose(fh);
    return;
  }

  if ((foutj = open_targetfile(output_dir)) == NULL) {
    fclose(fh);
    fclose(fd);
    return;
  }

  proc(fh, fd, foutj);

#ifdef DEBUG
  printf("\nprocess one ok");
#endif

  fclose(fh);
  fclose(fd);
  fclose(foutj);
}

inline static void
confgen(const char *input_dir, const char *output_dir)
{
  char inputname[256];
  strcpy(inputname, input_dir);
  char *fn = inputname + strlen(inputname);
#ifdef __LINUX__
  *fn++ = '/';

  DIR *dirp;
  struct dirent *dp;

  dirp = opendir(input_dir);
  if (dirp == NULL) {
    printf("open the input directory error\n");
    return;
  }

  for (;;) {
    dp = readdir(dirp);
    if (dp == NULL) break;
    if (dp->d_name[0] == '.') continue;

    size_t len = strlen(dp->d_name);
    if (len >= 3 && strcmp(".zk", dp->d_name + len - 3) == 0) {
      strcpy(fn, dp->d_name);
      proc_one(inputname, output_dir);
    }
  }
  closedir(dirp);
#endif

#ifdef __WIN32__
  *fn++ = '\\';

  struct _finddata_t fds;
  char pattern[256];
  strcpy(pattern, input_dir);
  size_t len = strlen(input_dir);
  pattern[len++] = '\\'; pattern[len++] = '*'; pattern[len++] = '.'; 
  pattern[len++] = 'z'; pattern[len++] = 'k';
  pattern[len] = '\0';
  long handle = _findfirst(pattern, &fds);
  if (handle != -1) {
    strcpy(fn, fds.name);
    proc_one(inputname, output_dir);
  }
  while (_findnext(handle, &fds) != -1L) {
    strcpy(fn, fds.name);
    proc_one(inputname, output_dir);
#ifdef DEBUG
    printf("windows: next file\n");
#endif
  }
  _findclose(handle);
#endif
}

int
main(int argc, char *argv[])
{
  if (argc != 3) {
    printf("usage: 2c headerfile outfile\n");
    return -1;
  }
  confgen(argv[1], argv[2]);
  return 0;
}

static struct type_st {
  int type;
  int cs;
  char name[MAX_VAR_LEN];
} types[MAX_TYPE_COUNT];
static int type_count = 0;

#define UNKNOWN_TYPE -1
static inline int
get_type(const char *type)
{
#ifdef DEBUG
  printf("type str:%s\n", type);
#endif
  for (int i = 0; i < TYPE_COUNT; ++i) {
    if (strcmp(type, data_type[i]) == 0)
      return i;
  }
  return UNKNOWN_TYPE;
}

static FILE *
open_file(const char *fn, const char *modes)
{
  FILE *f = fopen(fn, modes);
  if (f == NULL)
    fprintf(stderr, "%s cann't opened\n", fn);
  return f;
}

#define PREPARE_CONTENT_JAVA       \
  "package common.def.conf;\n"     \
  "import java.util.List;\n"       \
  "import java.util.ArrayList;\n"  \
  "import java.util.Map;\n"        \
  "import java.util.HashMap;\n\n" 

#define CLASS_HEADER_FMT_JAVA "public class %s {\n"

#define NEW_FIELD_FMT_JAVA "  public final %s %s;\n"

#define FIELD_FMT_JAVA                                \
  "  public static Map<Integer, %s> dic = "           \
  "new HashMap<Integer, %s>(128);\n"                  \
  "  public static List<%s> array = "                 \
  "new ArrayList<%s>(128);\n"                         \
  "  public static Map<Integer, %s> getDic() {"       \
  "return dic;}\n"                                    \
  "  public static List<%s> getArr() {return array;}"

static void
prepare_file(FILE *foutj)
{
  fprintf(foutj, PREPARE_CONTENT_JAVA);
}

static void
proc(FILE *fh, FILE *fd, FILE *foutj)
{
  proc_head(fh, foutj);
#ifdef DEBUG
  printf("head finished");
#endif
  proc_data(fd, foutj);
#ifdef DEBUG
  printf("data finished");
#endif
}

#define SERVER_NEED(cs) (cs[0] == 's' || cs[1] == 's')
#define CLIENT_NEED(cs) (cs[0] == 'c')
#define SERVER 0x1 
#define CLIENT 0x2

static void
parse_header(const char *type_name, const char *cs, struct type_st *type)
{
  type->type = get_type(type_name);
  type->cs = 0;
  type->cs |= SERVER_NEED(cs) ? SERVER : 0;
  type->cs |= CLIENT_NEED(cs) ? CLIENT : 0;
  if (type->type == UNKNOWN_TYPE)
    strncpy(type->name, type_name, MAX_VAR_LEN);
#ifdef DEBUG
  printf("cs: %s, cs int :%d,type: %d\n", cs,type->cs, type->type);
#endif
}

#define NEW_FIELD(foutj, type_st, vname)              \
  do {                                                \
    int cs = type_st->cs;                             \
    char *type_name = type_st->name;                  \
    int type = type_st->type;                         \
    if (cs & SERVER) {                                \
      fprintf(foutj, NEW_FIELD_FMT_JAVA,              \
          type == UNKNOWN_TYPE ? type_name :          \
          data_type_java[type], vname);               \
    }                                                 \
  } while(0)

#define CSTR_DEC(cstr_dec_java_ptr, type_st, vname)                  \
  do {                                                               \
    int cs = type_st->cs;                                            \
    char *type_name = type_st->name;                                 \
    int type = type_st->type;                                        \
    if (cs & SERVER)                                                 \
      cstr_dec_java_ptr += snprintf(cstr_dec_java_ptr,CSTR_LEN,      \
          "%s %s,", type == UNKNOWN_TYPE ? type_name :               \
          data_type_java[type], vname);                              \
  } while(0)

#define CSTR_DEF(cstr_java_ptr, name, cs)                    \
  do {                                                       \
    if (cs & SERVER)                                         \
      cstr_java_ptr += snprintf(cstr_java_ptr, CSTR_LEN,     \
          "    this.%s=%s;\n", name,name);                   \
  } while(0)

#define CSTR_END(fout, dec, def) \
  do {                           \
    fprintf(fout, "%s", dec);    \
    fprintf(fout, "%s", def);    \
    fprintf(fout, "  }\n");      \
  } while(0)

#define CSTR_LEN 2048

static void
proc_head(FILE *fh, FILE *foutj)
{
  prepare_file(foutj);
  fprintf(foutj, CLASS_HEADER_FMT_JAVA, class_name);
  fprintf(foutj, FIELD_FMT_JAVA, class_name,class_name,
      class_name,class_name,class_name,class_name);
  static char line[MAX_LINE_LEN],
    cstr_dec_java[CSTR_LEN], 
    cstr_def_java[CSTR_LEN];
  char *cstr_dec_java_ptr = cstr_dec_java,
       *cstr_def_java_ptr = cstr_def_java;
  cstr_dec_java_ptr += snprintf(cstr_dec_java_ptr, CSTR_LEN, "  public %s(", class_name);

  char *name_ptr, *cs_ptr, *type_ptr;
  
  type_count = 0;
  while (fgets(line, MAX_LINE_LEN, fh) != NULL) {
    name_ptr = line;
    type_ptr = strchr(name_ptr, ',') + 1;
    *(type_ptr - 1) = '\0';
    cs_ptr = strchr(type_ptr, ',') + 1;
    *(cs_ptr - 1) = '\0';
    struct type_st *type_st_ptr = types + type_count;
    parse_header(type_ptr, cs_ptr, type_st_ptr);
    NEW_FIELD(foutj, type_st_ptr, name_ptr);
    CSTR_DEC(cstr_dec_java_ptr, type_st_ptr, name_ptr);
    CSTR_DEF(cstr_def_java_ptr, name_ptr, type_st_ptr->cs);

    ++type_count;
  }
  *(cstr_dec_java_ptr - 1) = ')';
  *cstr_dec_java_ptr = '{';
  *(cstr_dec_java_ptr + 1) = '\n';
  *(cstr_dec_java_ptr + 2) = '\0';
  CSTR_END(foutj, cstr_dec_java, cstr_def_java);
}


static const char *
get_value(const char *value, int type)
{
#ifdef DEBUG
  printf("line:%d, value:%s, type:%d\n", __LINE__, value, type);
#endif
  if (type == UNKNOWN_TYPE) {
#ifdef DEBUG
    printf("value is %s, type is %d\n", value, type);
#endif
    return "null";
  }
  if (strlen(value) == 0 || strcmp(value, "") == 0)
    return default_value[type];
  if (type == BOOL)
    return *value == '0' ? "false" : "true";
  if (type == INT)
    return value;
  static char v[2048], vv;
  int idx = 0;
  if (type == FLOAT) {
    idx = strlen(value);
    strncpy(v, value, idx);
  } else if (type == ARR_INT) {
    while ((vv = *value++) != '\0') {
      if (vv == '\\' && *value != '\0' && *value == 'u' && 
          *(value + 1) != '\0' && *(value + 1) == '2' &&
          *(value + 2) != '\0' && *(value + 2) == 'c') {
        v[idx++] = ',';
        value += 3;
      } else v[idx++] = vv;
    }
  } else if (type == ARR_BOOL) {
    while ((vv = *value++) != '\0') {
      if (vv == '0') {
        memcpy(v + idx, "false", 5);
        idx += 5;
      } else if (vv == '1') {
        memcpy(v + idx, "true", 4);
        idx += 4;
      } else continue;
      if (*value != '\0')
        v[idx++] = ',';
    }
  } else if (type == ARR_FLOAT) {
    while ((vv = *value++) != '\0') {
      if (vv == '\\' && *value != '\0' && *value == 'u' && 
          *(value + 1) != '\0' && *(value + 1) == '2' &&
          *(value + 2) != '\0' && *(value + 2) == 'c') {
        v[idx++] = ',';
        value += 3;
      } else v[idx++] = vv;
    }
  } else if (type == STRING || type == ARR_STRING || type == DATE) {
    int isArr = type == ARR_STRING;
    v[idx++] = '"';
    while ((vv = *value++) != '\0') {
      if (vv == '\\') {
        if (*value != '\0' && *value == 'u') {
          if(*(value + 1) != '\0' && *(value + 1) == 'a') {
            v[idx++] = '\n';
            value += 2;
          } else if (*(value + 1) != '\0' && *(value + 1) == '2' &&
              *(value + 2) != '\0' && *(value + 2) == 'c') {
            if (isArr) v[idx++] = '"';
            v[idx++] = ',';
            if (isArr) v[idx++] = '"';
            value += 3;
          }
        } else v[idx++] = vv;
      } else v[idx++] = vv;
    }
    v[idx++] = '"';
  }
  v[idx] ='\0';
#ifdef DEBUG
  printf("value %s\n", v);
#endif
  return v;
}

#define ADD_FMT_JAVA                                  \
  "  private static void add%d() {\n"                 \
  "    %s item = new %s(%s);\n"                       \
  "    dic.put(item.id, item);\n"                     \
  "    array.add(item);}\n\n"

#define BEGIN_STATIC(foutj)           \
  fprintf(foutj, "  static {\n");     \

#define STATIC_ADD(foutj, cnt)        \
  do {                                       \
    for (int i = 0; i < cnt; ++i) {          \
      fprintf(foutj, "    add%d();\n", i);   \
    }                                        \
  } while (0)

#define END_STATIC(foutj)   \
    fprintf(foutj, "  }\n");       \

#define IS_ARRAY(type) (type == ARR_BOOL || type == ARR_INT || \
    type == ARR_FLOAT || type == ARR_STRING)

#define APPEND_ARG(args_ptr, type, value, data_type_str)        \
  do {                                                          \
    if (IS_ARRAY(type))                                         \
      args_ptr +=snprintf(args_ptr, MAX_LINE_LEN,               \
          "new %s{%s},", data_type_str[type], value);           \
    else                                                        \
      args_ptr +=snprintf(args_ptr, MAX_LINE_LEN,               \
          "%s,", value);                                        \
  } while(0)

#define ADD_FUN(foutj, args_j, no)                     \
  do {                                                 \
  fprintf(foutj, ADD_FMT_JAVA, no, class_name,         \
      class_name, args_j);                             \
  } while (0)

#define END_CLASS(foutj) fprintf(foutj, "}");

int is_comment(const char *line)
{
  char *last_comma = strrchr(line, ',');
  return *(last_comma + 1) == '1';
}

static void
proc_data(FILE *fd, FILE *foutj)
{
  static char line[MAX_LINE_LEN];
  static char args_java[MAX_LINE_LEN];
  int line_count = 0;
  while (fgets(line, MAX_LINE_LEN, fd) != NULL) {
#ifdef DEBUG
    printf("%s\n", line);
#endif
    if (is_comment(line)) continue;

    char *comma_ptr, *v_ptr = line;
    int type_idx = 0;
    char *args_ptr_java = args_java;
    while (type_idx < type_count && v_ptr != NULL) {
      comma_ptr = strchr(v_ptr, ',');
      if (comma_ptr != NULL) *comma_ptr = '\0';

      int type = types[type_idx].type;
      int cs = types[type_idx].cs;
#ifdef DEBUG
      printf("value of %s\n", get_value(v_ptr, type));
#endif
      if (cs & SERVER)
        APPEND_ARG(args_ptr_java, type, get_value(v_ptr,type), data_type_java);
      v_ptr = comma_ptr == NULL ? NULL : comma_ptr + 1;
      ++type_idx;
    }
    *(args_ptr_java - 1) = '\0';
    ADD_FUN(foutj, args_java, line_count);
#ifdef DEBUG
    printf("j: %s\n", args_java);
#endif
    ++line_count;
  }
  BEGIN_STATIC(foutj);
  STATIC_ADD(foutj, line_count);
  END_STATIC(foutj);
  END_CLASS(foutj);
}
