#ifndef WAV_PARSER_HPP_
#define WAV_PARSER_HPP_

class Wave_file{

	public:

		std::string file_name;
		std::ifstream file_in;

		bool big_endian = 0;
		uint32_t buff_size = 1<<16;

		char raw_riff_chunk[12] = {0},
			 raw_format_chunk[52] = {0},
			 raw_data_chunk[8] = {0},
			 subformat_fixed_string[14] = {0};
		
		char *buff = NULL;


		std::string chunk_id = "    ",
					wave_format = "    ",
					format_chunk_id = "    ",
					data_chunk_id = "    ";

		uint32_t chunk_size = 0,
				 format_chunk_size = 0,
				 audio_format = 0,
				 channel_amount = 0,
				 sample_rate = 0,
				 byte_rate = 0,
				 block_align = 0,
				 bits_per_sample = 0,
				 extension_size = 0,
				 valid_bits = 0,
				 channel_mask = 0,
				 subformat = 0,
				 data_chunk_size = 0,
				 sample_size = 0,
				 samples_per_channel = 0;



		/*
		   WAVE format reading is based on the contents of this site and
		   the other sites it links to:
		   http://www-mmsp.ece.mcgill.ca/Documents/AudioFormats/WAVE/WAVE.html
		   
		   raw_in_riff ->
		   guaranteed:
		   raw_chunk_id[4], big
		   raw_chunk_size[4], little
		   raw_format[4], big

		   raw_in_format ->
		   guaranteed:
		   raw_format_chunk_id[4], big
		   raw_format_chunk_size[4], little
		   raw_audio_format[2], little
		   raw_channel_amount[2], little
		   raw_sample_rate[4], little
		   raw_byte_rate[4], little 
		   raw_block_align[2], little
		   raw_bits_per_sample[2], little
		   expect:
		   raw_exstension_size[2], little
		   raw_valid_bits[2], little
		   raw_channel_mask[4], little
		   raw_subformat[16], little

		   expect:
		   raw_fact_chunk_id[4], big
		   raw_fact_chunk_size[4], little -> n
		   raw_fact_chunk_data[n], little

		   guaranteed:
		   raw_data_id[4], big
		   raw_data_size[4], little -> n
		   raw_data[n], little :)

		   some unexpected chunks may appear
		   after the RIFF chunk and can be ignored.
		   


		   Supported audio formats:
		   0x0001	PCM		(integer samples)
		   0x0003	IEEE	(float samples)

		   all supported audio formats can be handled as if they were
		   WAVE FORMAT EXTENSIBLE (0xfffe)
		   
		*/

		std::string exit(std::string message){
			file_in.close();
			return message;
		}

		int unexpected_chunk(std::string &id, std::string match){

			/*
			   return value:
			   0 -> chunk was expected
			   1 -> chunk was unexpected
			   2 -> chunk was bad (improperly formatted, corrupted, or something else)

			   reads & ignores an unexpected chunk, then reads the ID of the next chunk.
			*/

			if(id != match){

				char raw_uchunk_size[4];
				uint32_t uchunk_size;

				file_in.read(raw_uchunk_size, 4);
				if(!file_in.good()) return 2;

				memcpy(&uchunk_size, raw_uchunk_size, 4);

				for(uint32_t i=0; i<uchunk_size; i += buff_size){
					uint32_t read_size = std::min(buff_size, uchunk_size-i);
					char *raw_uchunk_data = new char[read_size];
					file_in.read(raw_uchunk_data, read_size);
					if(!file_in.good()) return 2;
				}

				char raw_new_chunk_id[4];
				file_in.read(raw_new_chunk_id, 4);
				memcpy((char *)id.c_str(), raw_new_chunk_id, 4);
				return 1;
			}
			return 0;
		}

		std::string initialize(){

			std::string message;
			int read_pos = 0;

			uint16_t temp1 = 0x0102;
			char *temp2 = (char *)&temp1;
			big_endian = (*temp2 == 1);
			if(big_endian) return exit("ERROR: PROGRAM IS RUN ON A BIG-ENDIAN SYSTEM");

			file_in.open(file_name);
			if(!file_in.good()) return exit("ERROR: FILE DOES NOT EXIST");

			file_in.read(raw_riff_chunk, 12);
			if(!file_in.good()) return exit("ERROR: BAD RIFF CHUNK");
		
			memcpy((char *)chunk_id.c_str(), raw_riff_chunk+read_pos, 4); read_pos += 4;
			memcpy(&chunk_size, raw_riff_chunk+read_pos, 4); read_pos += 4;
			memcpy((char *)wave_format.c_str(), raw_riff_chunk+read_pos, 4); read_pos += 4;

			if(chunk_id != "RIFF") return exit("ERROR: FILE IS NOT RIFF FORMAT: "+chunk_id);
			if(wave_format != "WAVE") return exit("ERROR: FILE IS NOT WAVE FORMAT: "+wave_format);

			read_pos = 0;

			file_in.read(raw_format_chunk+read_pos, 4);
			if(!file_in.good()) return exit("ERROR: BAD FORMAT CHUNK ID");
			memcpy((char *)format_chunk_id.c_str(), raw_format_chunk+read_pos, 4); read_pos += 4;

			while(1){
				int log = unexpected_chunk(format_chunk_id, "fmt ");
				if(log == 2) return exit("ERROR: BAD UNEXPECTED CHUNK BETWEEN RIFF AND FORMAT");
				if(log == 0) break;
			}

			file_in.read(raw_format_chunk+read_pos, 4);
			if(!file_in.good()) return exit("ERROR: BAD FORMAT CHUNK SIZE");
			memcpy(&format_chunk_size, raw_format_chunk+read_pos, 4); read_pos += 4;

			file_in.read(raw_format_chunk+read_pos, format_chunk_size);
			if(!file_in.good()) return exit("ERROR: BAD FORMAT CHUNK");

			memcpy(&audio_format, raw_format_chunk+read_pos, 2); read_pos += 2;
			memcpy(&channel_amount, raw_format_chunk+read_pos, 2); read_pos += 2;
			memcpy(&sample_rate, raw_format_chunk+read_pos, 4); read_pos += 4;
			memcpy(&byte_rate, raw_format_chunk+read_pos, 4); read_pos += 4;
			memcpy(&block_align, raw_format_chunk+read_pos, 2); read_pos += 2;
			memcpy(&bits_per_sample, raw_format_chunk+read_pos, 2); read_pos += 2;
			memcpy(&extension_size, raw_format_chunk+read_pos, 2); read_pos += 2;
			memcpy(&valid_bits, raw_format_chunk+read_pos, 2); read_pos += 2;
			memcpy(&channel_mask, raw_format_chunk+read_pos, 4); read_pos += 4;
			
			memcpy(&subformat, raw_format_chunk+read_pos, 2); read_pos += 2;
			memcpy(subformat_fixed_string, raw_format_chunk+read_pos, 14); read_pos += 14;

			buff_size *= block_align;
			sample_size = block_align/channel_amount;

			read_pos = 0;
			file_in.read(raw_data_chunk+read_pos, 4);
			if(!file_in.good()) return exit("ERROR: BAD DATA CHUNK ID");
			memcpy((char *)data_chunk_id.c_str(), raw_data_chunk+read_pos, 4); read_pos += 4;

			while(1){
				int log = unexpected_chunk(data_chunk_id, "data");
				if(log == 2) return exit("ERROR: BAD UNEXPECTED CHUNK BETWEEN FORMAT AND DATA");
				if(log == 0) break;
			}

			file_in.read(raw_data_chunk+read_pos, 4);
			if(!file_in.good()) return exit("ERROR: BAD DATA CHUNK SIZE");
			memcpy(&data_chunk_size, raw_data_chunk+read_pos, 4); read_pos += 4;

			samples_per_channel = data_chunk_size/block_align;

			std::vector<uint32_t> supported_audio_formats = {0x1, 0x3};
			bool audio_format_supported = 0;
			for(uint32_t i : supported_audio_formats){
				if(audio_format == i) audio_format_supported = 1;
			}

			if(audio_format == 0xfffe){
				// WAVE FORMAT EXTENSIBLE
				for(uint32_t i : supported_audio_formats){
					if(subformat == i) audio_format_supported = 1;
				}
			} else {
				subformat = audio_format;
			}

			if(channel_mask == 0){
				for(uint32_t i=0; i<channel_amount; i++) channel_mask |= (1<<i);
			}

			if(!audio_format_supported) return exit("ERROR: AUDIO FORMAT NOT SUPPORTED");

			message = "OK\nchunk_size "+std::to_string(chunk_size)
					+ "\nformat_chunk_size "+std::to_string(format_chunk_size)
					+ "\naudio_format "+std::to_string(audio_format)
					+ "\nchannel_amount "+std::to_string(channel_amount)
					+ "\nsample_rate "+std::to_string(sample_rate)
					+ "\nbyte_rate "+std::to_string(byte_rate)
					+ "\nblock_align "+std::to_string(block_align)
					+ "\nbits_per_sample "+std::to_string(bits_per_sample)
					+ "\nchannel_mask "+std::bitset<18>(channel_mask).to_string()
					+ "\naudio_subformat "+std::to_string(subformat)
					+ "\ndata_chunk_size "+std::to_string(data_chunk_size);

			return message;
		}

		bool read_samples(void *dest, uint32_t read_amount){

			/*
			   copy read_amount of blocks to dest.
			   one sample from each channel -> block.
			   example:
			   channel_amount = 2
			   read_amount = 3

			   {s00, s01, s10, s11, s20, s21} are copied to dest.

			*/

			if(!file_in.is_open()) return 0;

			if(buff == NULL) buff = new char[buff_size];

			for(uint32_t i = 0; i<read_amount*block_align; i+=buff_size){

				uint32_t read_size = std::min(buff_size, read_amount*block_align-i);
				file_in.read(buff, read_size);

				if(!file_in.good()){
					exit("");
					return 0;
				}

				memcpy((char *)dest+i, buff, read_size);
			}

			if(!file_in.good()){
				exit("");
				return 0;
			}
			return 1;
		}


		Wave_file(std::string file_name_){
			file_name = file_name_;
		}
};
#endif
