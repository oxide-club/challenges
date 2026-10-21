
../../../challenges/015-mystery-program/materials/mystery-linux-x86_64:     file format elf64-x86-64


Disassembly of section .init:

0000000000001000 <_init>:
    1000:	f3 0f 1e fa          	endbr64
    1004:	48 83 ec 08          	sub    rsp,0x8
    1008:	48 8b 05 c1 2f 00 00 	mov    rax,QWORD PTR [rip+0x2fc1]        # 3fd0 <__gmon_start__>
    100f:	48 85 c0             	test   rax,rax
    1012:	74 02                	je     1016 <_init+0x16>
    1014:	ff d0                	call   rax
    1016:	48 83 c4 08          	add    rsp,0x8
    101a:	c3                   	ret

Disassembly of section .plt:

0000000000001020 <ferror@plt-0x10>:
    1020:	ff 35 ca 2f 00 00    	push   QWORD PTR [rip+0x2fca]        # 3ff0 <_GLOBAL_OFFSET_TABLE_+0x8>
    1026:	ff 25 cc 2f 00 00    	jmp    QWORD PTR [rip+0x2fcc]        # 3ff8 <_GLOBAL_OFFSET_TABLE_+0x10>
    102c:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]

0000000000001030 <ferror@plt>:
    1030:	ff 25 ca 2f 00 00    	jmp    QWORD PTR [rip+0x2fca]        # 4000 <ferror@GLIBC_2.2.5>
    1036:	68 00 00 00 00       	push   0x0
    103b:	e9 e0 ff ff ff       	jmp    1020 <_init+0x20>

0000000000001040 <fread@plt>:
    1040:	ff 25 c2 2f 00 00    	jmp    QWORD PTR [rip+0x2fc2]        # 4008 <fread@GLIBC_2.2.5>
    1046:	68 01 00 00 00       	push   0x1
    104b:	e9 d0 ff ff ff       	jmp    1020 <_init+0x20>

0000000000001050 <__stack_chk_fail@plt>:
    1050:	ff 25 ba 2f 00 00    	jmp    QWORD PTR [rip+0x2fba]        # 4010 <__stack_chk_fail@GLIBC_2.4>
    1056:	68 02 00 00 00       	push   0x2
    105b:	e9 c0 ff ff ff       	jmp    1020 <_init+0x20>

0000000000001060 <__sysv_signal@plt>:
    1060:	ff 25 b2 2f 00 00    	jmp    QWORD PTR [rip+0x2fb2]        # 4018 <__sysv_signal@GLIBC_2.2.5>
    1066:	68 03 00 00 00       	push   0x3
    106b:	e9 b0 ff ff ff       	jmp    1020 <_init+0x20>

0000000000001070 <fflush@plt>:
    1070:	ff 25 aa 2f 00 00    	jmp    QWORD PTR [rip+0x2faa]        # 4020 <fflush@GLIBC_2.2.5>
    1076:	68 04 00 00 00       	push   0x4
    107b:	e9 a0 ff ff ff       	jmp    1020 <_init+0x20>

0000000000001080 <exit@plt>:
    1080:	ff 25 a2 2f 00 00    	jmp    QWORD PTR [rip+0x2fa2]        # 4028 <exit@GLIBC_2.2.5>
    1086:	68 05 00 00 00       	push   0x5
    108b:	e9 90 ff ff ff       	jmp    1020 <_init+0x20>

0000000000001090 <fwrite@plt>:
    1090:	ff 25 9a 2f 00 00    	jmp    QWORD PTR [rip+0x2f9a]        # 4030 <fwrite@GLIBC_2.2.5>
    1096:	68 06 00 00 00       	push   0x6
    109b:	e9 80 ff ff ff       	jmp    1020 <_init+0x20>

Disassembly of section .text:

00000000000010a0 <_start>:
    10a0:	f3 0f 1e fa          	endbr64
    10a4:	31 ed                	xor    ebp,ebp
    10a6:	49 89 d1             	mov    r9,rdx
    10a9:	5e                   	pop    rsi
    10aa:	48 89 e2             	mov    rdx,rsp
    10ad:	48 83 e4 f0          	and    rsp,0xfffffffffffffff0
    10b1:	50                   	push   rax
    10b2:	54                   	push   rsp
    10b3:	45 31 c0             	xor    r8d,r8d
    10b6:	31 c9                	xor    ecx,ecx
    10b8:	48 8d 3d c9 01 00 00 	lea    rdi,[rip+0x1c9]        # 1288 <main>
    10bf:	ff 15 fb 2e 00 00    	call   QWORD PTR [rip+0x2efb]        # 3fc0 <__libc_start_main@GLIBC_2.34>
    10c5:	f4                   	hlt
    10c6:	66 2e 0f 1f 84 00 00 	cs nop WORD PTR [rax+rax*1+0x0]
    10cd:	00 00 00 

00000000000010d0 <deregister_tm_clones>:
    10d0:	48 8d 3d 71 2f 00 00 	lea    rdi,[rip+0x2f71]        # 4048 <__TMC_END__>
    10d7:	48 8d 05 6a 2f 00 00 	lea    rax,[rip+0x2f6a]        # 4048 <__TMC_END__>
    10de:	48 39 f8             	cmp    rax,rdi
    10e1:	74 15                	je     10f8 <deregister_tm_clones+0x28>
    10e3:	48 8b 05 de 2e 00 00 	mov    rax,QWORD PTR [rip+0x2ede]        # 3fc8 <_ITM_deregisterTMCloneTable>
    10ea:	48 85 c0             	test   rax,rax
    10ed:	74 09                	je     10f8 <deregister_tm_clones+0x28>
    10ef:	ff e0                	jmp    rax
    10f1:	0f 1f 80 00 00 00 00 	nop    DWORD PTR [rax+0x0]
    10f8:	c3                   	ret
    10f9:	0f 1f 80 00 00 00 00 	nop    DWORD PTR [rax+0x0]

0000000000001100 <register_tm_clones>:
    1100:	48 8d 3d 41 2f 00 00 	lea    rdi,[rip+0x2f41]        # 4048 <__TMC_END__>
    1107:	48 8d 35 3a 2f 00 00 	lea    rsi,[rip+0x2f3a]        # 4048 <__TMC_END__>
    110e:	48 29 fe             	sub    rsi,rdi
    1111:	48 89 f0             	mov    rax,rsi
    1114:	48 c1 ee 3f          	shr    rsi,0x3f
    1118:	48 c1 f8 03          	sar    rax,0x3
    111c:	48 01 c6             	add    rsi,rax
    111f:	48 d1 fe             	sar    rsi,1
    1122:	74 14                	je     1138 <register_tm_clones+0x38>
    1124:	48 8b 05 ad 2e 00 00 	mov    rax,QWORD PTR [rip+0x2ead]        # 3fd8 <_ITM_registerTMCloneTable>
    112b:	48 85 c0             	test   rax,rax
    112e:	74 08                	je     1138 <register_tm_clones+0x38>
    1130:	ff e0                	jmp    rax
    1132:	66 0f 1f 44 00 00    	nop    WORD PTR [rax+rax*1+0x0]
    1138:	c3                   	ret
    1139:	0f 1f 80 00 00 00 00 	nop    DWORD PTR [rax+0x0]

0000000000001140 <__do_global_dtors_aux>:
    1140:	f3 0f 1e fa          	endbr64
    1144:	80 3d 3d 2f 00 00 00 	cmp    BYTE PTR [rip+0x2f3d],0x0        # 4088 <completed.0>
    114b:	75 33                	jne    1180 <__do_global_dtors_aux+0x40>
    114d:	55                   	push   rbp
    114e:	48 83 3d 8a 2e 00 00 	cmp    QWORD PTR [rip+0x2e8a],0x0        # 3fe0 <__cxa_finalize@GLIBC_2.2.5>
    1155:	00 
    1156:	48 89 e5             	mov    rbp,rsp
    1159:	74 0d                	je     1168 <__do_global_dtors_aux+0x28>
    115b:	48 8b 3d de 2e 00 00 	mov    rdi,QWORD PTR [rip+0x2ede]        # 4040 <__dso_handle>
    1162:	ff 15 78 2e 00 00    	call   QWORD PTR [rip+0x2e78]        # 3fe0 <__cxa_finalize@GLIBC_2.2.5>
    1168:	e8 63 ff ff ff       	call   10d0 <deregister_tm_clones>
    116d:	c6 05 14 2f 00 00 01 	mov    BYTE PTR [rip+0x2f14],0x1        # 4088 <completed.0>
    1174:	5d                   	pop    rbp
    1175:	c3                   	ret
    1176:	66 2e 0f 1f 84 00 00 	cs nop WORD PTR [rax+rax*1+0x0]
    117d:	00 00 00 
    1180:	c3                   	ret
    1181:	0f 1f 40 00          	nop    DWORD PTR [rax+0x0]
    1185:	66 66 2e 0f 1f 84 00 	data16 cs nop WORD PTR [rax+rax*1+0x0]
    118c:	00 00 00 00 

0000000000001190 <frame_dummy>:
    1190:	f3 0f 1e fa          	endbr64
    1194:	e9 67 ff ff ff       	jmp    1100 <register_tm_clones>

0000000000001199 <fail>:
    1199:	55                   	push   rbp
    119a:	48 89 e5             	mov    rbp,rsp
    119d:	48 8b 05 dc 2e 00 00 	mov    rax,QWORD PTR [rip+0x2edc]        # 4080 <stderr@GLIBC_2.2.5>
    11a4:	48 8d 3d 5d 0e 00 00 	lea    rdi,[rip+0xe5d]        # 2008 <_IO_stdin_used+0x8>
    11ab:	48 89 c1             	mov    rcx,rax
    11ae:	ba 20 00 00 00       	mov    edx,0x20
    11b3:	be 01 00 00 00       	mov    esi,0x1
    11b8:	e8 d3 fe ff ff       	call   1090 <fwrite@plt>
    11bd:	bf 01 00 00 00       	mov    edi,0x1
    11c2:	e8 b9 fe ff ff       	call   1080 <exit@plt>

00000000000011c7 <output>:
    11c7:	55                   	push   rbp
    11c8:	48 89 e5             	mov    rbp,rsp
    11cb:	48 83 ec 10          	sub    rsp,0x10
    11cf:	48 89 7d f8          	mov    QWORD PTR [rbp-0x8],rdi
    11d3:	48 89 75 f0          	mov    QWORD PTR [rbp-0x10],rsi
    11d7:	48 8b 0d 82 2e 00 00 	mov    rcx,QWORD PTR [rip+0x2e82]        # 4060 <stdout@GLIBC_2.2.5>
    11de:	48 8b 55 f0          	mov    rdx,QWORD PTR [rbp-0x10]
    11e2:	48 8b 45 f8          	mov    rax,QWORD PTR [rbp-0x8]
    11e6:	be 01 00 00 00       	mov    esi,0x1
    11eb:	48 89 c7             	mov    rdi,rax
    11ee:	e8 9d fe ff ff       	call   1090 <fwrite@plt>
    11f3:	48 39 45 f0          	cmp    QWORD PTR [rbp-0x10],rax
    11f7:	74 05                	je     11fe <output+0x37>
    11f9:	e8 9b ff ff ff       	call   1199 <fail>
    11fe:	90                   	nop
    11ff:	c9                   	leave
    1200:	c3                   	ret

0000000000001201 <finish>:
    1201:	55                   	push   rbp
    1202:	48 89 e5             	mov    rbp,rsp
    1205:	48 8b 05 54 2e 00 00 	mov    rax,QWORD PTR [rip+0x2e54]        # 4060 <stdout@GLIBC_2.2.5>
    120c:	48 89 c7             	mov    rdi,rax
    120f:	e8 5c fe ff ff       	call   1070 <fflush@plt>
    1214:	85 c0                	test   eax,eax
    1216:	75 13                	jne    122b <finish+0x2a>
    1218:	48 8b 05 41 2e 00 00 	mov    rax,QWORD PTR [rip+0x2e41]        # 4060 <stdout@GLIBC_2.2.5>
    121f:	48 89 c7             	mov    rdi,rax
    1222:	e8 09 fe ff ff       	call   1030 <ferror@plt>
    1227:	85 c0                	test   eax,eax
    1229:	74 05                	je     1230 <finish+0x2f>
    122b:	e8 69 ff ff ff       	call   1199 <fail>
    1230:	90                   	nop
    1231:	5d                   	pop    rbp
    1232:	c3                   	ret

0000000000001233 <readall>:
    1233:	55                   	push   rbp
    1234:	48 89 e5             	mov    rbp,rsp
    1237:	48 8b 05 32 2e 00 00 	mov    rax,QWORD PTR [rip+0x2e32]        # 4070 <stdin@GLIBC_2.2.5>
    123e:	48 8d 3d 5b 2e 00 00 	lea    rdi,[rip+0x2e5b]        # 40a0 <data>
    1245:	48 89 c1             	mov    rcx,rax
    1248:	ba 01 00 01 00       	mov    edx,0x10001
    124d:	be 01 00 00 00       	mov    esi,0x1
    1252:	e8 e9 fd ff ff       	call   1040 <fread@plt>
    1257:	48 89 05 4a 2e 01 00 	mov    QWORD PTR [rip+0x12e4a],rax        # 140a8 <len>
    125e:	48 8b 05 0b 2e 00 00 	mov    rax,QWORD PTR [rip+0x2e0b]        # 4070 <stdin@GLIBC_2.2.5>
    1265:	48 89 c7             	mov    rdi,rax
    1268:	e8 c3 fd ff ff       	call   1030 <ferror@plt>
    126d:	85 c0                	test   eax,eax
    126f:	75 0f                	jne    1280 <readall+0x4d>
    1271:	48 8b 05 30 2e 01 00 	mov    rax,QWORD PTR [rip+0x12e30]        # 140a8 <len>
    1278:	48 3d 00 00 01 00    	cmp    rax,0x10000
    127e:	76 05                	jbe    1285 <readall+0x52>
    1280:	e8 14 ff ff ff       	call   1199 <fail>
    1285:	90                   	nop
    1286:	5d                   	pop    rbp
    1287:	c3                   	ret

0000000000001288 <main>:
    1288:	55                   	push   rbp
    1289:	48 89 e5             	mov    rbp,rsp
    128c:	48 83 ec 70          	sub    rsp,0x70
    1290:	89 7d 9c             	mov    DWORD PTR [rbp-0x64],edi
    1293:	48 89 75 90          	mov    QWORD PTR [rbp-0x70],rsi
    1297:	64 48 8b 04 25 28 00 	mov    rax,QWORD PTR fs:0x28
    129e:	00 00 
    12a0:	48 89 45 f8          	mov    QWORD PTR [rbp-0x8],rax
    12a4:	31 c0                	xor    eax,eax
    12a6:	be 01 00 00 00       	mov    esi,0x1
    12ab:	bf 0d 00 00 00       	mov    edi,0xd
    12b0:	e8 ab fd ff ff       	call   1060 <__sysv_signal@plt>
    12b5:	83 7d 9c 01          	cmp    DWORD PTR [rbp-0x64],0x1
    12b9:	74 05                	je     12c0 <main+0x38>
    12bb:	e8 d9 fe ff ff       	call   1199 <fail>
    12c0:	e8 6e ff ff ff       	call   1233 <readall>
    12c5:	48 8b 05 dc 2d 01 00 	mov    rax,QWORD PTR [rip+0x12ddc]        # 140a8 <len>
    12cc:	48 83 f8 40          	cmp    rax,0x40
    12d0:	76 05                	jbe    12d7 <main+0x4f>
    12d2:	e8 c2 fe ff ff       	call   1199 <fail>
    12d7:	48 c7 45 a8 00 00 00 	mov    QWORD PTR [rbp-0x58],0x0
    12de:	00 
    12df:	eb 36                	jmp    1317 <main+0x8f>
    12e1:	48 8d 15 b8 2d 00 00 	lea    rdx,[rip+0x2db8]        # 40a0 <data>
    12e8:	48 8b 45 a8          	mov    rax,QWORD PTR [rbp-0x58]
    12ec:	48 01 d0             	add    rax,rdx
    12ef:	0f b6 00             	movzx  eax,BYTE PTR [rax]
    12f2:	83 f0 5a             	xor    eax,0x5a
    12f5:	89 c2                	mov    edx,eax
    12f7:	48 8b 45 a8          	mov    rax,QWORD PTR [rbp-0x58]
    12fb:	89 c1                	mov    ecx,eax
    12fd:	48 8b 05 a4 2d 01 00 	mov    rax,QWORD PTR [rip+0x12da4]        # 140a8 <len>
    1304:	48 2b 45 a8          	sub    rax,QWORD PTR [rbp-0x58]
    1308:	48 83 e8 01          	sub    rax,0x1
    130c:	01 ca                	add    edx,ecx
    130e:	88 54 05 b0          	mov    BYTE PTR [rbp+rax*1-0x50],dl
    1312:	48 83 45 a8 01       	add    QWORD PTR [rbp-0x58],0x1
    1317:	48 8b 05 8a 2d 01 00 	mov    rax,QWORD PTR [rip+0x12d8a]        # 140a8 <len>
    131e:	48 39 45 a8          	cmp    QWORD PTR [rbp-0x58],rax
    1322:	72 bd                	jb     12e1 <main+0x59>
    1324:	48 8b 15 7d 2d 01 00 	mov    rdx,QWORD PTR [rip+0x12d7d]        # 140a8 <len>
    132b:	48 8d 45 b0          	lea    rax,[rbp-0x50]
    132f:	48 89 d6             	mov    rsi,rdx
    1332:	48 89 c7             	mov    rdi,rax
    1335:	e8 8d fe ff ff       	call   11c7 <output>
    133a:	e8 c2 fe ff ff       	call   1201 <finish>
    133f:	b8 00 00 00 00       	mov    eax,0x0
    1344:	48 8b 55 f8          	mov    rdx,QWORD PTR [rbp-0x8]
    1348:	64 48 2b 14 25 28 00 	sub    rdx,QWORD PTR fs:0x28
    134f:	00 00 
    1351:	74 05                	je     1358 <main+0xd0>
    1353:	e8 f8 fc ff ff       	call   1050 <__stack_chk_fail@plt>
    1358:	c9                   	leave
    1359:	c3                   	ret

Disassembly of section .fini:

000000000000135c <_fini>:
    135c:	f3 0f 1e fa          	endbr64
    1360:	48 83 ec 08          	sub    rsp,0x8
    1364:	48 83 c4 08          	add    rsp,0x8
    1368:	c3                   	ret
